"""
test_crypto.py
==============
Automated tests for the Hybrid Cryptography System
Run: python test_crypto.py
"""

import os
import sys
import hashlib
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
import hybrid_crypto as hc

KEYS_DIR = Path(tempfile.gettempdir()) / "hcrypt_test_keys"


class TestKeyGeneration(unittest.TestCase):
    """Tests for RSA key pair generation."""

    def test_generate_keypair_returns_pem(self):
        priv, pub = hc.generate_rsa_keypair(1024)
        self.assertIn(b"BEGIN RSA PRIVATE KEY", priv + b"BEGIN PRIVATE KEY")
        self.assertTrue(len(pub) > 100)

    def test_save_keypair_creates_files(self):
        KEYS_DIR.mkdir(exist_ok=True)
        priv_path = str(KEYS_DIR / "private.pem")
        pub_path  = str(KEYS_DIR / "public.pem")
        meta = hc.save_keypair(priv_path, pub_path, bits=1024)
        self.assertTrue(os.path.exists(priv_path))
        self.assertTrue(os.path.exists(pub_path))
        self.assertIn("fingerprint", meta)
        self.assertEqual(meta["key_size_bits"], 1024)

    def test_fingerprint_is_sha256_hex(self):
        KEYS_DIR.mkdir(exist_ok=True)
        meta = hc.save_keypair(
            str(KEYS_DIR / "p.pem"),
            str(KEYS_DIR / "pub.pem"),
            bits=1024
        )
        self.assertEqual(len(meta["fingerprint"]), 64)


class TestEncryptDecrypt(unittest.TestCase):
    """Encrypt → Decrypt roundtrip tests."""

    @classmethod
    def setUpClass(cls):
        KEYS_DIR.mkdir(exist_ok=True)
        cls.priv_key = str(KEYS_DIR / "private.pem")
        cls.pub_key  = str(KEYS_DIR / "public.pem")
        hc.save_keypair(cls.priv_key, cls.pub_key, bits=1024)
        cls.tmp_dir  = Path(tempfile.gettempdir()) / "hcrypt_test_files"
        cls.tmp_dir.mkdir(exist_ok=True)

    def _roundtrip(self, content: bytes, label: str):
        plain_path   = str(self.tmp_dir / f"{label}_plain.dat")
        enc_path     = str(self.tmp_dir / f"{label}.enc")
        dec_path     = str(self.tmp_dir / f"{label}_dec.dat")

        with open(plain_path, "wb") as f:
            f.write(content)

        enc_meta = hc.encrypt_file(plain_path, enc_path, self.pub_key)
        self.assertEqual(enc_meta["status"], "encrypted")
        self.assertTrue(os.path.exists(enc_path))

        dec_meta = hc.decrypt_file(enc_path, dec_path, self.priv_key)
        self.assertEqual(dec_meta["status"], "decrypted")

        with open(dec_path, "rb") as f:
            recovered = f.read()

        self.assertEqual(content, recovered, f"Roundtrip failed for {label}")
        original_hash = hashlib.sha256(content).hexdigest()
        self.assertEqual(original_hash, dec_meta["sha256"])

    def test_empty_file(self):
        self._roundtrip(b"", "empty")

    def test_small_text(self):
        self._roundtrip(b"Hello, Hybrid Cryptography!", "small_text")

    def test_multiline_text(self):
        data = b"Line 1\nLine 2\nLine 3\nSensitive data here!\n" * 10
        self._roundtrip(data, "multiline")

    def test_binary_data(self):
        import secrets
        data = secrets.token_bytes(4096)
        self._roundtrip(data, "binary_4k")

    def test_large_file(self):
        import secrets
        data = secrets.token_bytes(1024 * 512)   # 512 KB
        self._roundtrip(data, "large_512k")


class TestIntegrity(unittest.TestCase):
    """HMAC tamper-detection tests."""

    @classmethod
    def setUpClass(cls):
        KEYS_DIR.mkdir(exist_ok=True)
        cls.priv_key = str(KEYS_DIR / "private.pem")
        cls.pub_key  = str(KEYS_DIR / "public.pem")
        if not os.path.exists(cls.priv_key):
            hc.save_keypair(cls.priv_key, cls.pub_key, bits=1024)
        cls.tmp_dir  = Path(tempfile.gettempdir()) / "hcrypt_test_integrity"
        cls.tmp_dir.mkdir(exist_ok=True)

    def test_tampered_file_detected(self):
        plain_path = str(self.tmp_dir / "secret.txt")
        enc_path   = str(self.tmp_dir / "secret.enc")
        dec_path   = str(self.tmp_dir / "secret_dec.txt")

        with open(plain_path, "wb") as f:
            f.write(b"Top secret message")

        hc.encrypt_file(plain_path, enc_path, self.pub_key)

        # Tamper with the encrypted file (flip bits near the end)
        with open(enc_path, "r+b") as f:
            f.seek(-10, 2)
            data = f.read(10)
            f.seek(-10, 2)
            f.write(bytes(b ^ 0xFF for b in data))

        with self.assertRaises(ValueError):
            hc.decrypt_file(enc_path, dec_path, self.priv_key)

    def test_verify_returns_verified_on_clean_file(self):
        plain_path = str(self.tmp_dir / "clean.txt")
        enc_path   = str(self.tmp_dir / "clean.enc")

        with open(plain_path, "wb") as f:
            f.write(b"Clean file content")

        hc.encrypt_file(plain_path, enc_path, self.pub_key)
        result = hc.verify_file_integrity(enc_path, self.priv_key)
        self.assertIn("VERIFIED", result["integrity"])


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Hybrid Crypto System -- Automated Test Suite")
    print("="*60 + "\n")
    unittest.main(verbosity=2)
