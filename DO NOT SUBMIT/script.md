# 🎬 Presentation & Demo Script
## Secure File Encryption System using Hybrid Cryptography
### Information Security — Group Project

> **Total Duration**: ~8–10 minutes  
> **Format**: Screen-recorded live demonstration  
# 🧑 MEMBER 1 — Waqas Ul Hasan
## Part 1: Introduction & Theory (4 minutes)

---

### 🎙️ SLIDE 1 — Title Slide (0:00–0:20)

> *[Screen shows title slide with project name and group names]*

**"Hello everyone. My name is Waqas Ul Hasan, and together with my teammate Qurat Ul ain, we present our Information Security project — a Secure File Encryption System using Hybrid Cryptography."**

---

### 🎙️ SLIDE 2 — Problem Statement (0:20–1:00)

> *[Slide: Why do we need this?]*

**"In today's digital world, sensitive files — whether medical records, financial documents, or personal data — are constantly at risk of interception. The question is: how do we protect files while transmitting or storing them?"**

**"We need an encryption system that is:**
- **Secure** — resistant to brute force and cryptanalysis
- **Efficient** — can handle files of any size
- **Verifiable** — detects tampering before decryption"**

**"This is exactly what our Hybrid Cryptography System provides."**

---

### 🎙️ SLIDE 3 — What is Hybrid Cryptography? (1:00–2:00)

> *[Slide: Venn diagram or comparison table]*

**"Let me explain why we use a hybrid approach."**

**"Symmetric encryption — like AES — is extremely fast. It can encrypt gigabytes of data in milliseconds. However, it has a critical problem: both the sender and receiver need the same secret key. How do you share that key securely?"**

**"Asymmetric encryption — like RSA — solves this. You publish your public key, anyone can encrypt with it, but only your private key can decrypt. However, RSA is computationally heavy and can only encrypt tiny amounts of data directly."**

**"The solution? Combine them:"**
- **AES encrypts the file** — fast, efficient
- **RSA encrypts only the AES key** — secure key exchange
- **Result: Best of both worlds**"**

---

### 🎙️ SLIDE 4 — Technical Algorithms (2:00–3:00)

> *[Slide: Algorithm specs table]*

**"Our system uses three cryptographic mechanisms:"**

**"First — AES-256-CBC. AES stands for Advanced Encryption Standard, a NIST-approved symmetric cipher. We use 256-bit keys in CBC (Cipher Block Chaining) mode. Each block of data is XOR'd with the previous ciphertext block before encryption, hiding patterns in the data."**

**"Second — RSA-2048 with OAEP padding. RSA is an asymmetric cipher based on the mathematical difficulty of factoring large prime numbers. The 2048-bit key means an attacker would need to factor a number with 617 decimal digits. OAEP padding adds randomness, protecting against padding oracle attacks."**

**"Third — HMAC-SHA256 for integrity verification. A Hash-based Message Authentication Code ensures that any modification to the encrypted file is detected before decryption is even attempted."**

---

### 🎙️ SLIDE 5 — System Architecture & Methodology (3:00–4:00)

> *[Slide: Encryption flow diagram]*

**"Here is our encryption methodology:"**

**"When you encrypt a file:**
1. We generate a **random 256-bit AES key** and a **random 16-byte IV** — unique for each encryption
2. The file is **encrypted with AES-256-CBC** producing the ciphertext
3. We compute **HMAC-SHA256** over the IV and ciphertext — creating an integrity tag
4. The AES key is **encrypted with the recipient's RSA public key** using OAEP
5. Everything is **bundled into a .enc file**: magic header, encrypted key, IV, HMAC tag, and ciphertext"**

**"This is called the Encrypt-then-MAC paradigm — the provably secure order of operations."**

---

### 🎙️ SLIDE 6 — Core Implementation (4:00–4:30)

> *[Slide: Core Implementation code block]*

**"Here you can see the core Python implementation using the PyCryptodome library."**

**"We generate the 256-bit AES key and 128-bit IV using a Cryptographically Secure Pseudorandom Number Generator. The file is encrypted using AES in CBC mode with PKCS7 padding. We then generate the HMAC-SHA256 tag over the IV and ciphertext. Finally, the AES session key is encrypted using the recipient's RSA public key with OAEP padding."**

**"Our codebase is cleanly structured into separate modules, separating the core cryptography engine from the CLI and the PyQt6 Desktop App interfaces."**

**"I'll now hand over to Qurat Ul ain who will demonstrate the system live."**

---

---

# 🧑 MEMBER 2 — Qurat Ul ain
## Part 2: Live Demo, Results & Security Analysis (4–5 minutes)

---

### 🎙️ SLIDE 7 — Live Demo Introduction (4:30–4:50)

> *[Slide: Live Demonstration]*
> *[Transition to screen share showing project folder]*

**"Thank you Waqas. I'm Qurat Ul ain. I'll now demonstrate our system live. We have built a full desktop application with a clean, modern interface — as well as a command-line interface. Let me start with the CLI to show exactly what's happening, then launch the app."**

---

### 🎙️ DEMO 1 — Installing Dependencies (4:20–4:40)

> *[Terminal open in IS-Terminal directory]*

**"Let's start. First, I'll install the required library — PyCryptodome."**

```
pip install -r requirements.txt
```

**"The requirements file includes PyCryptodome for cryptographic operations, Colorama for colored terminal output, and tqdm for progress bars. Installation takes just a few seconds."**

---

### 🎙️ DEMO 2 — Key Generation (4:40–5:10)

> *[Run in src/ directory]*

**"Now let's generate our RSA key pair."**

```bash
cd src
python cli.py keygen --private ../keys/private.pem --public ../keys/public.pem
```

**"The system generates a 2048-bit RSA key pair. Notice the output shows the key size, file paths, and a SHA-256 fingerprint of the public key — useful for verification. The private key is saved locally and must never be shared. The public key can be freely distributed."**

> *[Show the keys/ folder with the two .pem files]*

**"You can see two files created: private.pem and public.pem."**

---

### 🎙️ DEMO 3 — Encrypting a File (5:10–5:50)

> *[Create a sample file first]*

**"Let me create a sample sensitive file."**

```bash
echo "TOP SECRET: Bank account details - Account: 1234567890, PIN: 9876" > ../samples/secret.txt
```

**"Now let's encrypt it using the recipient's public key."**

```bash
python cli.py encrypt --input ../samples/secret.txt --output ../samples/secret.enc --key ../keys/public.pem
```

**"Look at the output — it shows the encryption algorithm used, the original and encrypted sizes, and the SHA-256 hash of the original file. Notice the encrypted file is slightly larger due to the RSA-encrypted key header and HMAC tag."**

> *[Open secret.enc in a hex editor or show it's unreadable]*

**"If I try to open this encrypted file, you see it's completely unreadable — just binary data. The contents are perfectly hidden."**

---

### 🎙️ DEMO 4 — Decrypting the File (5:50–6:30)

**"Now let's decrypt it using the private key."**

```bash
python cli.py decrypt --input ../samples/secret.enc --output ../samples/recovered.txt --key ../keys/private.pem
```

**"The system automatically verifies the HMAC integrity tag first. Since the file hasn't been tampered with, decryption proceeds successfully. The output confirms integrity is VERIFIED."**

```bash
type ../samples/recovered.txt
```

**"And there's our original content — perfectly recovered, byte for byte."**

---

### 🎙️ DEMO 5 — Tamper Detection (6:30–7:10)

> *[This is the most impressive demo — shows security]*

**"Now let me demonstrate one of the most important security features — tamper detection."**

**"I'll simulate an attacker modifying the encrypted file."**

```python
# Quick tamper simulation in Python
python -c "
f = open('../samples/secret.enc', 'r+b')
f.seek(-10, 2)
data = f.read(10)
f.seek(-10, 2)
f.write(bytes(b ^ 0xFF for b in data))
f.close()
print('File tampered!')
"
```

**"Now if we try to decrypt the tampered file..."**

```bash
python cli.py decrypt --input ../samples/secret.enc --output ../samples/tampered_dec.txt --key ../keys/private.pem
```

**"The system immediately detects the tampering! The HMAC verification fails and decryption is aborted. The error message says: INTEGRITY CHECK FAILED. This is the Encrypt-then-MAC pattern in action."**

---

### 🎙️ SLIDE 8 — Desktop App Demonstration (7:10–7:40)

> *[Slide: Desktop Application]*
> *[Switch screen to show the PyQt6 desktop app]*

**"We also packaged this into a full desktop application — no terminal needed."**

```bash
python app.py
```

**"The app has five pages in a clean sidebar: Dashboard, Key Generation, Encrypt, Decrypt, and Verify. Let me quickly demonstrate the same encrypt-decrypt flow using just clicks."**

> *[Navigate to Key Generation page, click Generate — keys appear in log]*

> *[Navigate to Encrypt page, browse for secret.txt, browse for public key, click Encrypt]*

> *[Navigate to Decrypt page, browse for secret.enc, browse for private key, click Decrypt — log shows HMAC verified]*

**"Every operation runs on a background thread so the UI never freezes, and the output log at the bottom shows exactly what's happening in real time."**

**"We also packaged this into a standalone exe — no Python installation required — just double-click and it runs."**

```
dist\HybridCrypto.exe
```

---

### 🎙️ SLIDE 9 — Test Results (7:40–8:10)

> *[Run tests or show test output screenshot]*

**"We ran a comprehensive automated test suite covering:"**
- **Empty files, small text files, binary data, and 512KB large files**
- **Encrypt-Decrypt roundtrip** with SHA-256 hash verification
- **Tamper detection** on all file sizes

```bash
cd ..
python test_crypto.py
```

**"All tests pass. The SHA-256 hashes before encryption and after decryption match exactly in every case."**

---

### 🎙️ SLIDE 10 — Security Analysis (8:10–8:45)

> *[Slide: Security analysis table]*

**"Let's analyze the security of our system:"**

**"Against brute force — AES-256 has 2^256 possible keys. Even with all the world's computing power, breaking it would take longer than the age of the universe."**

**"Against chosen-ciphertext attacks — OAEP padding on RSA prevents these attacks which could otherwise recover the private key."**

**"Against replay attacks — each encryption uses a fresh random IV and AES key, so encrypting the same file twice produces completely different ciphertext."**

**"Against tampering — HMAC-SHA256 guarantees that any single-bit modification to the ciphertext is detected. An attacker cannot forge a valid HMAC without the secret AES key."**

---

### 🎙️ SLIDE 11 — Conclusion (8:45–9:15)

**"In conclusion, our Secure File Encryption System successfully demonstrates hybrid cryptography in a practical, usable tool."**

**"We combined RSA-2048 for secure key exchange, AES-256-CBC for fast and secure file encryption, and HMAC-SHA256 for integrity verification."**

**"The system is delivered as a full PyQt6 desktop application with a modern dark interface, a CLI for power users, and an automated test suite with 10 passing tests. It's also packaged as a standalone .exe that runs on any Windows machine without Python."**

**"Future improvements could include: adding a passphrase to protect the private key, implementing digital signatures for sender authentication, and adding support for encrypting for multiple recipients simultaneously."**

**"Thank you for your attention. We're happy to answer any questions."**

---

## 📋 Demo Commands Quick Reference

```bash
# Navigate to project
cd c:\FA23-BCS-A\IS\IS-Terminal

# Install dependencies
pip install -r requirements.txt

# --- OPTION A: Desktop App ---
python app.py
# Or just double-click:
# dist\HybridCrypto.exe

# --- OPTION B: CLI ---
cd src

# Generate keys
python cli.py keygen --private ../keys/private.pem --public ../keys/public.pem

# Encrypt
python cli.py encrypt --input ../samples/secret.txt --output ../samples/secret.enc --key ../keys/public.pem

# Decrypt
python cli.py decrypt --input ../samples/secret.enc --output ../samples/recovered.txt --key ../keys/private.pem

# Verify integrity
python cli.py verify --input ../samples/secret.enc --key ../keys/private.pem

# Run tests
cd ..
python test_crypto.py
```

---

## ⚠️ Pre-Demo Checklist

- [ ] Python 3.8+ installed
- [ ] `pip install -r requirements.txt` done
- [ ] `samples/` directory created manually or via `mkdir samples`
- [ ] Screen recording software ready
- [ ] Font size in terminal increased for visibility (>14pt)
- [ ] Dark terminal theme for better contrast

---

*Script prepared for IS Project Recording — May 2026*
