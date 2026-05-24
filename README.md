# Secure File Encryption System 🔐

A comprehensive file encryption system implementing **Hybrid Cryptography** to ensure data confidentiality, integrity, and secure key exchange. The project combines the speed of symmetric encryption with the security of asymmetric encryption, making it capable of securely transmitting files of any size over insecure networks.

## Features

- **Confidentiality (AES-256-CBC)**: Ultra-fast symmetric encryption for the core file data.
- **Secure Key Exchange (RSA-2048 OAEP)**: Asymmetric encryption used exclusively to securely wrap and transmit the AES session key.
- **Data Integrity (HMAC-SHA256)**: Implements the provably secure *Encrypt-then-MAC* paradigm to detect any tampering before decryption is attempted.
- **Pattern Concealment**: A Cryptographically Secure Pseudo-Random Number Generator (CSPRNG) provides unique 128-bit Initialization Vectors (IVs) for every encryption.
- **Dual Interface**: Includes a modern **PyQt6 Desktop Application** with threaded operations, as well as a powerful command-line interface (CLI).

## Architecture

The project is modularly structured, separating the core cryptography engine from the user interfaces:

```text
├── app.py                      # PyQt6 Desktop GUI entry point
├── dist/HybridCrypto.exe       # Standalone Windows executable
├── src/
│   ├── hybrid_crypto.py        # Core cryptography engine
│   └── cli.py                  # Command-line interface
├── keys/                       # Directory for RSA .pem keys
├── samples/                    # Directory for test files
├── test_crypto.py              # Automated test suite (10 unit tests)
└── requirements.txt            # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8 or higher installed on your system.

### Setup
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Waqas-Ul-Hasan/HybridCrypto.git
cd HybridCrypto
pip install -r requirements.txt
```

*Note: The primary dependencies are `pycryptodome` (for cryptographic primitives) and `PyQt6` (for the desktop UI).*

## Usage

### 1. Desktop Application (GUI)
The most user-friendly way to use the system is via the graphical dashboard. Heavy cryptographic tasks are offloaded to background threads to keep the interface perfectly smooth.

Run the app via Python:
```bash
python app.py
```

Alternatively, if you are on Windows, you can just double-click the compiled standalone executable without needing Python installed:
```cmd
dist\HybridCrypto.exe
```

### 2. Command Line Interface (CLI)
For power users and scripting, a complete CLI is provided.

**Navigate to the source directory:**
```bash
cd src
```

**Generate an RSA Key Pair:**
```bash
python cli.py keygen --private ../keys/private.pem --public ../keys/public.pem
```

**Encrypt a File:**
```bash
python cli.py encrypt --input ../samples/secret.txt --output ../samples/secret.enc --key ../keys/public.pem
```
*This produces an unreadable `.enc` bundle containing the encrypted AES key, IV, HMAC tag, and ciphertext.*

**Decrypt a File:**
```bash
python cli.py decrypt --input ../samples/secret.enc --output ../samples/recovered.txt --key ../keys/private.pem
```
*The system will automatically verify the HMAC integrity tag first. If the file was tampered with, decryption will be aborted.*

## Testing
The project includes a comprehensive automated test suite that validates encryption against empty files, small text, large binary data (512KB+), and rigorously tests the tamper detection logic.

```bash
python test_crypto.py
```
*All tests verify that the pre-encryption and post-decryption SHA-256 hashes match exactly.*

## Authors
- **Waqas Ul Hasan** (FA23-BCS-167)
- **Qurat Ul ain** (FA23-BCS-195)
