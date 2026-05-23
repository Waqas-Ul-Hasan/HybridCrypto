"""
hybrid_crypto.py
================
Secure File Encryption System using Hybrid Cryptography
Combines RSA-2048 (asymmetric) + AES-256-CBC (symmetric) + HMAC-SHA256 (integrity)

Authors  : Group Project - Information Security
Algorithm: Hybrid Encryption
           1. Generate random AES-256 session key
           2. Encrypt file data with AES-256-CBC
           3. Encrypt AES key with RSA-2048 public key
           4. Bundle: [RSA-encrypted key | IV | HMAC | AES-encrypted data]
"""

import os
import struct
import hmac
import hashlib
import json
import base64
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Cryptographic primitives (pure-stdlib fallback + pycryptodome preferred)
# ---------------------------------------------------------------------------
try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256 as CryptoSHA256
    from Crypto.Random import get_random_bytes
    from Crypto.Util.Padding import pad, unpad
    CRYPTO_BACKEND = "pycryptodome"
except ImportError:
    # Fallback: cryptography library
    from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
    from cryptography.hazmat.primitives import hashes, padding as sym_padding, serialization
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    import secrets
    CRYPTO_BACKEND = "cryptography"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAGIC          = b"HCRYPT10"   # 8-byte file magic
RSA_KEY_SIZE   = 2048          # bits
AES_KEY_SIZE   = 32            # bytes (256-bit)
AES_IV_SIZE    = 16            # bytes
HMAC_SIZE      = 32            # bytes (SHA-256)
ENC_KEY_SIZE   = RSA_KEY_SIZE // 8   # 256 bytes for 2048-bit RSA


# ===========================================================================
#  Key Generation
# ===========================================================================

def generate_rsa_keypair(bits: int = RSA_KEY_SIZE) -> tuple[bytes, bytes]:
    """
    Generate an RSA key pair.
    Returns (private_key_pem, public_key_pem) as bytes.
    """
    if CRYPTO_BACKEND == "pycryptodome":
        key = RSA.generate(bits)
        private_pem = key.export_key(format="PEM")
        public_pem  = key.publickey().export_key(format="PEM")
    else:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=bits,
            backend=default_backend()
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    return private_pem, public_pem


def save_keypair(private_path: str, public_path: str, bits: int = RSA_KEY_SIZE) -> dict:
    """
    Generate and persist an RSA key pair to disk.
    Returns metadata dict.
    """
    private_pem, public_pem = generate_rsa_keypair(bits)

    Path(private_path).parent.mkdir(parents=True, exist_ok=True)
    Path(public_path).parent.mkdir(parents=True, exist_ok=True)

    with open(private_path, "wb") as f:
        f.write(private_pem)
    with open(public_path, "wb") as f:
        f.write(public_pem)

    # Compute key fingerprint (SHA-256 of public key)
    fingerprint = hashlib.sha256(public_pem).hexdigest()

    return {
        "backend"      : CRYPTO_BACKEND,
        "key_size_bits": bits,
        "private_key"  : private_path,
        "public_key"   : public_path,
        "fingerprint"  : fingerprint,
        "generated_at" : datetime.utcnow().isoformat() + "Z",
    }


# ===========================================================================
#  Encryption
# ===========================================================================

def encrypt_file(input_path: str, output_path: str, public_key_path: str) -> dict:
    """
    Encrypt a file using hybrid cryptography.

    File format (.enc):
        [MAGIC 8B][ENC_KEY_SIZE_2B][ENC_KEY Nb][AES_IV 16B][HMAC 32B][CIPHERTEXT ...]

    Returns metadata dict with encryption details.
    """
    # -- Read plaintext
    with open(input_path, "rb") as f:
        plaintext = f.read()

    # -- Load RSA public key
    with open(public_key_path, "rb") as f:
        pub_pem = f.read()

    # -- Generate random AES session key + IV
    if CRYPTO_BACKEND == "pycryptodome":
        aes_key = get_random_bytes(AES_KEY_SIZE)
        iv      = get_random_bytes(AES_IV_SIZE)

        # AES-256-CBC encrypt
        cipher_aes   = AES.new(aes_key, AES.MODE_CBC, iv)
        ciphertext   = cipher_aes.encrypt(pad(plaintext, AES.block_size))

        # RSA-OAEP encrypt the AES key (using Crypto.Hash.SHA256, NOT hashlib)
        rsa_key       = RSA.import_key(pub_pem)
        cipher_rsa    = PKCS1_OAEP.new(rsa_key, hashAlgo=CryptoSHA256)
        encrypted_key = cipher_rsa.encrypt(aes_key)

    else:
        aes_key = secrets.token_bytes(AES_KEY_SIZE)
        iv      = secrets.token_bytes(AES_IV_SIZE)

        # AES-256-CBC encrypt (with PKCS7 padding)
        padder    = sym_padding.PKCS7(128).padder()
        padded    = padder.update(plaintext) + padder.finalize()
        cipher_aes = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        enc       = cipher_aes.encryptor()
        ciphertext = enc.update(padded) + enc.finalize()

        # RSA-OAEP encrypt
        pub_key = serialization.load_pem_public_key(pub_pem, backend=default_backend())
        encrypted_key = pub_key.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    # -- HMAC-SHA256 over IV + ciphertext (integrity tag)
    mac = hmac.new(aes_key, iv + ciphertext, hashlib.sha256).digest()

    # -- Build output bundle
    enc_key_len = len(encrypted_key)
    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack(">H", enc_key_len))   # 2 bytes big-endian
        f.write(encrypted_key)
        f.write(iv)
        f.write(mac)
        f.write(ciphertext)

    # -- Compute SHA-256 of original file for verification record
    original_hash = hashlib.sha256(plaintext).hexdigest()

    return {
        "status"         : "encrypted",
        "backend"        : CRYPTO_BACKEND,
        "input_file"     : input_path,
        "output_file"    : output_path,
        "original_size"  : len(plaintext),
        "encrypted_size" : os.path.getsize(output_path),
        "aes_mode"       : "AES-256-CBC",
        "rsa_mode"       : "RSA-2048-OAEP-SHA256",
        "integrity"      : "HMAC-SHA256",
        "original_hash"  : original_hash,
        "encrypted_at"   : datetime.utcnow().isoformat() + "Z",
    }


# ===========================================================================
#  Decryption
# ===========================================================================

def decrypt_file(input_path: str, output_path: str, private_key_path: str) -> dict:
    """
    Decrypt a .enc file produced by encrypt_file().
    Returns metadata dict with decryption details and integrity status.
    Raises ValueError on tampered/corrupt data.
    """
    with open(input_path, "rb") as f:
        data = f.read()

    # -- Parse bundle
    offset = 0
    magic  = data[offset:offset+8]; offset += 8
    if magic != MAGIC:
        raise ValueError(f"Invalid file format. Magic header mismatch: {magic!r}")

    enc_key_len = struct.unpack(">H", data[offset:offset+2])[0]; offset += 2
    encrypted_key = data[offset:offset+enc_key_len];             offset += enc_key_len
    iv            = data[offset:offset+AES_IV_SIZE];             offset += AES_IV_SIZE
    stored_mac    = data[offset:offset+HMAC_SIZE];               offset += HMAC_SIZE
    ciphertext    = data[offset:]

    # -- Load RSA private key
    with open(private_key_path, "rb") as f:
        priv_pem = f.read()

    # -- Decrypt AES session key with RSA private key
    if CRYPTO_BACKEND == "pycryptodome":
        rsa_key    = RSA.import_key(priv_pem)
        cipher_rsa = PKCS1_OAEP.new(rsa_key, hashAlgo=CryptoSHA256)
        aes_key    = cipher_rsa.decrypt(encrypted_key)

        # -- Verify HMAC integrity BEFORE decryption (Encrypt-then-MAC)
        computed_mac = hmac.new(aes_key, iv + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(stored_mac, computed_mac):
            raise ValueError("INTEGRITY CHECK FAILED: File may have been tampered with!")

        # -- AES-256-CBC decrypt
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        plaintext  = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)

    else:
        priv_key = serialization.load_pem_private_key(priv_pem, password=None, backend=default_backend())
        aes_key  = priv_key.decrypt(
            encrypted_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # -- Verify HMAC
        computed_mac = hmac.new(aes_key, iv + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(stored_mac, computed_mac):
            raise ValueError("INTEGRITY CHECK FAILED: File may have been tampered with!")

        # -- AES-256-CBC decrypt
        cipher_aes = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        dec        = cipher_aes.decryptor()
        padded     = dec.update(ciphertext) + dec.finalize()
        unpadder   = sym_padding.PKCS7(128).unpadder()
        plaintext  = unpadder.update(padded) + unpadder.finalize()

    # -- Write plaintext
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(plaintext)

    decrypted_hash = hashlib.sha256(plaintext).hexdigest()

    return {
        "status"        : "decrypted",
        "backend"       : CRYPTO_BACKEND,
        "input_file"    : input_path,
        "output_file"   : output_path,
        "decrypted_size": len(plaintext),
        "integrity"     : "VERIFIED [OK]",
        "sha256"        : decrypted_hash,
        "decrypted_at"  : datetime.utcnow().isoformat() + "Z",
    }


# ===========================================================================
#  Integrity-only verification (without decrypting plaintext)
# ===========================================================================

def verify_file_integrity(enc_path: str, private_key_path: str) -> dict:
    """
    Verify the HMAC tag of an encrypted file without writing the plaintext.
    Returns a dict with 'integrity' key: 'VERIFIED' or 'TAMPERED'.
    """
    try:
        # We reuse decrypt but write to a temp path, then delete
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        decrypt_file(enc_path, tmp_path, private_key_path)
        os.remove(tmp_path)
        return {"integrity": "VERIFIED [OK]", "file": enc_path}
    except ValueError as e:
        return {"integrity": "TAMPERED [!!]", "file": enc_path, "error": str(e)}
    except Exception as e:
        return {"integrity": "ERROR", "file": enc_path, "error": str(e)}
