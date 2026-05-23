# 🧪 Testing Guide: Hybrid Crypto System

This guide explains how to thoroughly test the Secure File Encryption System to ensure it works correctly under all conditions. You can use these tests during your viva to prove the system is robust and secure.

---

## 1. Automated Testing Suite

We have built a comprehensive unit test suite in `test_crypto.py` that automatically tests edge cases, large files, and tamper detection. 

### How to run it:
```bash
# From the root directory (IS-Terminal)
python test_crypto.py
```

### What is happening behind the scenes?
When you run this script, it executes 10 separate, isolated tests in a temporary directory:
1. **Empty File Test**: Ensures the system doesn't crash when encrypting a file with 0 bytes.
2. **Small/Multiline Text Test**: Verifies standard text files encrypt and decrypt without corruption.
3. **Binary Data Test**: Creates a 4 KB random binary file (like an image or PDF) and verifies it handles non-text data perfectly.
4. **Large File Test**: Creates a 512 KB file, encrypts, and decrypts it to verify AES-256 handles bulk data quickly and correctly.
5. **SHA-256 Hash Match**: For *every* file tested, it computes the hash of the original file and the decrypted file. If they don't match exactly, the test fails.
6. **Tamper Detection Test**: Encrypts a file, manually flips a random bit in the `.enc` ciphertext, and then attempts to decrypt it. It verifies that the HMAC validation catches the tampering and throws an error instead of decrypting garbage data.

---

## 2. Manual Testing (Desktop App)

To show the app visually, run the Desktop App:
```bash
python app.py 
# Or double-click dist\HybridCrypto.exe
```

### Case A: The "Happy Path" (Everything works)
1. **Generate Keys**: Go to the **Key Generation** tab. Generate a 2048-bit key. You will see `private.pem` and `public.pem` generated.
2. **Encrypt**: Go to the **Encrypt** tab. 
   - Select `samples/secret.txt` as input.
   - Set output to `samples/secret.enc`.
   - Select `keys/public.pem` as the key.
   - **What happens**: The system generates a random AES key, encrypts the file with AES-256, encrypts the AES key with RSA-2048, computes the HMAC, and saves the `.enc` bundle.
3. **Decrypt**: Go to the **Decrypt** tab.
   - Select `samples/secret.enc` as input.
   - Set output to `samples/recovered.txt`.
   - Select `keys/private.pem`.
   - **What happens**: The system verifies the HMAC. Since it's untouched, it decrypts the AES key using your private key, then decrypts the file back to `recovered.txt`.

### Case B: Tamper Detection (The Security Demo)
1. After completing Case A, open `samples/secret.enc` in Notepad.
2. Delete a single random character from the middle of the file and save it (this simulates a network attacker modifying the file).
3. Go back to the Desktop App and try to **Decrypt** or **Verify** the modified `secret.enc`.
4. **What happens**: The app will display a bright red **INTEGRITY FAILED** badge. The HMAC tag inside the file no longer matches the tampered ciphertext, so the app refuses to decrypt it, protecting you from malicious data.

---

## 3. Manual Testing (CLI)

If you prefer testing via the terminal, here are the commands to manually verify the system.

```bash
# 1. Generate keys
python src/cli.py keygen --private keys/private.pem --public keys/public.pem

# 2. Create a test file
echo "Top secret data" > secret_test.txt

# 3. Encrypt it
python src/cli.py encrypt --input secret_test.txt --output secret.enc --key keys/public.pem

# 4. Verify integrity (Before tampering)
python src/cli.py verify --input secret.enc --key keys/private.pem
# Result: [OK] INTEGRITY: VERIFIED

# 5. Tamper with the file (using Python to flip a bit)
python -c "f = open('secret.enc', 'r+b'); f.seek(-10, 2); d = f.read(1); f.seek(-10, 2); f.write(bytes([d[0] ^ 0xFF])); f.close()"

# 6. Verify integrity (After tampering)
python src/cli.py verify --input secret.enc --key keys/private.pem
# Result: [!!] INTEGRITY: TAMPERED

# 7. Attempt Decryption (Will fail safely)
python src/cli.py decrypt --input secret.enc --output recovered.txt --key keys/private.pem
# Result: [ERROR] INTEGRITY CHECK FAILED — file may have been tampered with!
```

---

## What to highlight during a Viva/Demo?
- **Speed**: Show how fast the 512KB automated test runs (AES is fast).
- **Security**: The tamper detection is the most impressive part. Flipping a single bit destroys the HMAC, proving the "Encrypt-then-MAC" architecture works flawlessly. 
- **Verifiability**: Highlighting that the SHA-256 hash of the decrypted file perfectly matches the original file proves zero data loss occurred during the cryptography process.
