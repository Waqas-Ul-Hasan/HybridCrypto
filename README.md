# 🔐 Secure File Encryption System using Hybrid Cryptography

> **Course**: Information Security | **Group Project** | 2 Members  
> **Tools**: Python 3.x, PyCryptodome, PyQt6, PyInstaller  
> **Algorithms**: RSA-2048 + AES-256-CBC + HMAC-SHA256

---

## 📌 What Is This Project?

This project implements a **Hybrid Cryptography System** for secure file encryption. Hybrid cryptography combines the best of two worlds:

| Type | Algorithm | Purpose |
|------|-----------|---------|
| **Asymmetric** | RSA-2048 | Securely exchange the AES session key |
| **Symmetric** | AES-256-CBC | Encrypt the actual file (fast & efficient) |
| **Integrity** | HMAC-SHA256 | Detect any tampering with the encrypted file |

### 🤔 Why Hybrid? — The Core Problem It Solves

- **RSA alone** is too slow for large files (can only encrypt ~214 bytes with 2048-bit key)
- **AES alone** has a key distribution problem (how do you securely share the key?)
- **Hybrid** = AES encrypts the data (fast), RSA encrypts only the AES key (secure)

---

## 🏗️ Project Structure

```
IS-Terminal/
├── app.py                 ← ⭐ PyQt6 desktop app (run this)
├── src/
│   ├── hybrid_crypto.py   ← Core encryption engine (RSA + AES + HMAC)
│   ├── cli.py             ← Command-line interface
│   └── gui.py             ← Legacy Tkinter GUI
├── dist/
│   └── HybridCrypto.exe   ← Standalone Windows executable (no Python needed)
├── keys/                  ← Generated RSA key files (auto-created)
├── samples/               ← Demo files
├── test_crypto.py         ← Automated test suite
├── generate_report.py     ← Regenerates the Word report
├── HybridCrypto.spec      ← PyInstaller build configuration
├── requirements.txt       ← Python dependencies
├── README.md              ← This file
├── script.md              ← Presentation script
├── report/                ← Word research report
└── presentation/          ← HTML presentation slides
```

---

## ⚙️ How It Works — Step by Step

### Encryption Process

```
INPUT FILE
    │
    ▼
[1] Generate random AES-256 key (32 bytes) + IV (16 bytes)
    │
    ├──► [2] Encrypt FILE with AES-256-CBC → CIPHERTEXT
    │
    ├──► [3] Compute HMAC-SHA256(IV + CIPHERTEXT) → MAC TAG
    │
    └──► [4] Encrypt AES key with RSA-2048 public key → ENCRYPTED KEY
                              │
                              ▼
                     [5] Bundle into .enc file:
                     ┌─────────────────────────┐
                     │ MAGIC HEADER (8 bytes)  │
                     │ ENCRYPTED AES KEY       │
                     │ AES IV (16 bytes)       │
                     │ HMAC TAG (32 bytes)     │
                     │ CIPHERTEXT (variable)   │
                     └─────────────────────────┘
```

### Decryption Process

```
.enc FILE
    │
    ▼
[1] Parse bundle: extract encrypted key, IV, HMAC, ciphertext
    │
    ▼
[2] Decrypt AES key using RSA-2048 PRIVATE KEY
    │
    ▼
[3] Verify HMAC-SHA256 → if mismatch, ABORT (tampered!)
    │
    ▼
[4] Decrypt ciphertext with AES-256-CBC → PLAINTEXT
    │
    ▼
OUTPUT FILE (identical to original)
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "from Crypto.PublicKey import RSA; print('PyCryptodome OK')"
```

---

## 💻 Usage

### Option A: Desktop App (PyQt6) ⭐ Recommended

```bash
python app.py
```

The app has a clean sidebar with 5 pages:
1. **Dashboard** — Architecture overview, algorithm cards, encryption flow
2. **Key Generation** — Generate RSA key pairs with 1024/2048/4096-bit selector
3. **Encrypt** — Browse input file + public key → produces `.enc` bundle
4. **Decrypt** — Browse `.enc` file + private key → HMAC verified before decryption
5. **Verify** — Visual pass/fail badge showing HMAC integrity status

#### Or just double-click the pre-built .exe (no Python needed)
```
dist\HybridCrypto.exe
```
To rebuild it yourself:
```bash
pyinstaller HybridCrypto.spec
# Output: dist/HybridCrypto.exe  (~43 MB, self-contained)
```

---

### Option B: Command-Line Interface (CLI)

```bash
cd src

# Step 1 — Generate keys
python cli.py keygen --private ../keys/private.pem --public ../keys/public.pem

# Step 2 — Encrypt
python cli.py encrypt --input ../samples/secret.txt --output ../samples/secret.enc --key ../keys/public.pem

# Step 3 — Decrypt
python cli.py decrypt --input ../samples/secret.enc --output ../samples/recovered.txt --key ../keys/private.pem

# Step 4 — Verify integrity
python cli.py verify --input ../samples/secret.enc --key ../keys/private.pem
```

---

## 🧪 Running Tests

```bash
python test_crypto.py
```

Tests cover:
- ✅ RSA key generation (1024, 2048, 4096-bit)
- ✅ Encrypt → Decrypt roundtrip (text, binary, large files)
- ✅ Empty file handling
- ✅ Tamper detection (HMAC failure)
- ✅ File integrity verification

---

## 🔒 Security Analysis — Viva Key Points

| Aspect | Detail |
|--------|--------|
| **Confidentiality** | AES-256-CBC encrypts data; brute-force impossible (2^256 keys) |
| **Key Security** | RSA-2048 OAEP protects AES key; RSA private key never transmitted |
| **Integrity** | HMAC-SHA256 detects any 1-bit change; computed before decryption |
| **Padding** | PKCS7 for AES; OAEP (SHA-256) for RSA — prevents padding oracle attacks |
| **IV Randomness** | Fresh random IV every encryption; prevents pattern leakage |
| **Encrypt-then-MAC** | MAC computed over ciphertext (not plaintext) — provably secure order |

### Potential Weaknesses (acknowledge in viva)
- Private key file must be kept secret (no passphrase in current impl.)
- No perfect forward secrecy (RSA key reuse)
- No key revocation mechanism
- Side-channel attacks possible at OS level

---

## 🎓 Viva Preparation FAQ

**Q: Why use RSA + AES instead of just RSA?**  
A: RSA is computationally expensive and limited in the amount of data it can encrypt directly (≈214 bytes for 2048-bit key). AES is extremely fast and can handle arbitrary file sizes. Hybrid uses each where it's strongest.

**Q: What is OAEP padding in RSA?**  
A: OAEP (Optimal Asymmetric Encryption Padding) adds randomness to RSA encryption, preventing deterministic outputs and protecting against chosen-ciphertext attacks. It uses SHA-256 as the hash function.

**Q: Why Encrypt-then-MAC and not MAC-then-Encrypt?**  
A: Encrypt-then-MAC is provably secure. If we MAC the plaintext and then encrypt, an attacker can modify ciphertext without the MAC detecting it. With EtM, any modification to the ciphertext causes HMAC verification to fail before decryption.

**Q: What is CBC mode?**  
A: Cipher Block Chaining — each plaintext block is XOR'd with the previous ciphertext block before encryption. This prevents identical plaintext blocks from producing identical ciphertext blocks, hiding data patterns.

**Q: What is the role of the IV (Initialization Vector)?**  
A: The IV makes the first block encryption non-deterministic. Without it, the same file encrypted twice with the same key produces identical ciphertext, leaking that files are the same. The IV is randomly generated each time and stored with the ciphertext (it doesn't need to be secret).

**Q: How does HMAC detect tampering?**  
A: HMAC-SHA256 produces a 32-byte authentication tag using the AES key + the ciphertext. Any single-bit change to the ciphertext produces a completely different HMAC. Without the secret key, an attacker cannot forge a valid HMAC.

**Q: What is the file format of the .enc output?**  
A: `[8-byte MAGIC] [2-byte key length] [RSA-encrypted AES key] [16-byte IV] [32-byte HMAC] [variable ciphertext]`

**Q: Which Python library did you use and why?**  
A: PyCryptodome — a well-maintained, actively developed cryptographic library for Python implementing production-grade algorithms. It's widely used in security tools.

---

## 📚 References

1. Stallings, W. (2017). *Cryptography and Network Security: Principles and Practice* (7th ed.)
2. Bellare, M., & Rogaway, P. (1994). Optimal Asymmetric Encryption — OAEP
3. NIST FIPS 197 — Advanced Encryption Standard (AES)
4. NIST SP 800-38A — Recommendation for Block Cipher Modes of Operation
5. RFC 2104 — HMAC: Keyed-Hashing for Message Authentication
6. PyCryptodome Documentation: https://pycryptodome.readthedocs.io

---

*Prepared for Information Security Course — Group Project*
