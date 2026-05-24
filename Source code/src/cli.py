"""
cli.py
======
Command-Line Interface for the Secure File Encryption System
Usage:
    python cli.py keygen  --private keys/private.pem --public keys/public.pem
    python cli.py encrypt --input secret.txt --output secret.enc --key keys/public.pem
    python cli.py decrypt --input secret.enc --output recovered.txt --key keys/private.pem
    python cli.py verify  --input secret.enc --key keys/private.pem
"""

import argparse
import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows to avoid cp1252 issues
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

import hybrid_crypto as hc


# ---------------------------------------------------------------------------
# Pretty printing helpers
# ---------------------------------------------------------------------------

def _c(text: str, color: str = "") -> str:
    if not COLOR:
        return text
    colors = {
        "green" : Fore.GREEN,
        "red"   : Fore.RED,
        "cyan"  : Fore.CYAN,
        "yellow": Fore.YELLOW,
        "bold"  : Style.BRIGHT,
        "reset" : Style.RESET_ALL,
    }
    return colors.get(color, "") + str(text) + Style.RESET_ALL


def _banner():
    banner = (
        "\n"
        "  +======================================================+\n"
        "  |   Secure File Encryption System - Hybrid Crypto     |\n"
        "  |   RSA-2048 + AES-256-CBC + HMAC-SHA256              |\n"
        "  +======================================================+\n"
    )
    print(_c(banner, "cyan"))


def _print_result(meta: dict, title: str):
    line = "  " + "-"*52
    print()
    print(_c(line, "cyan"))
    print(_c(f"  [OK]  {title}", "green"))
    print(_c(line, "cyan"))
    for k, v in meta.items():
        key_str = _c(f"  {k:<22}", "yellow")
        val_str = _c(str(v), "bold")
        print(f"{key_str}: {val_str}")
    print()


def _print_error(msg: str):
    print(_c(f"\n  [ERROR] {msg}\n", "red"))


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def cmd_keygen(args):
    print(_c("  [*] Generating RSA key pair...", "cyan"))
    try:
        meta = hc.save_keypair(args.private, args.public, bits=args.bits)
        _print_result(meta, "RSA Key Pair Generated")
        print(_c(f"  Private key -> {args.private}", "green"))
        print(_c(f"  Public  key -> {args.public}\n", "green"))
    except Exception as e:
        _print_error(str(e))
        sys.exit(1)


def cmd_encrypt(args):
    if not Path(args.input).exists():
        _print_error(f"Input file not found: {args.input}")
        sys.exit(1)
    if not Path(args.key).exists():
        _print_error(f"Public key not found: {args.key}")
        sys.exit(1)

    print(_c(f"  [*] Encrypting '{args.input}'...", "cyan"))
    try:
        meta = hc.encrypt_file(args.input, args.output, args.key)
        _print_result(meta, "File Encrypted Successfully")
    except Exception as e:
        _print_error(str(e))
        sys.exit(1)


def cmd_decrypt(args):
    if not Path(args.input).exists():
        _print_error(f"Encrypted file not found: {args.input}")
        sys.exit(1)
    if not Path(args.key).exists():
        _print_error(f"Private key not found: {args.key}")
        sys.exit(1)

    print(_c(f"  [*] Decrypting '{args.input}'...", "cyan"))
    try:
        meta = hc.decrypt_file(args.input, args.output, args.key)
        _print_result(meta, "File Decrypted Successfully")
    except ValueError as e:
        _print_error(str(e))
        sys.exit(1)
    except Exception as e:
        _print_error(str(e))
        sys.exit(1)


def cmd_verify(args):
    if not Path(args.input).exists():
        _print_error(f"Encrypted file not found: {args.input}")
        sys.exit(1)

    print(_c(f"  [*] Verifying integrity of '{args.input}'...", "cyan"))
    result = hc.verify_file_integrity(args.input, args.key)

    if "VERIFIED" in result["integrity"]:
        print(_c(f"\n  [OK] INTEGRITY: {result['integrity']}\n", "green"))
    else:
        print(_c(f"\n  [!!] INTEGRITY: {result['integrity']}\n", "red"))
        if "error" in result:
            print(_c(f"     {result['error']}\n", "red"))


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python cli.py",
        description="Secure File Encryption System using Hybrid Cryptography",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # keygen
    p_keygen = sub.add_parser("keygen", help="Generate RSA key pair")
    p_keygen.add_argument("--private", default="keys/private.pem", help="Path to save private key")
    p_keygen.add_argument("--public",  default="keys/public.pem",  help="Path to save public key")
    p_keygen.add_argument("--bits",    type=int, default=2048,      help="RSA key size (default 2048)")

    # encrypt
    p_enc = sub.add_parser("encrypt", help="Encrypt a file")
    p_enc.add_argument("--input",  required=True, help="Path to plaintext file")
    p_enc.add_argument("--output", required=True, help="Path for encrypted output (.enc)")
    p_enc.add_argument("--key",    required=True, help="Path to RSA public key")

    # decrypt
    p_dec = sub.add_parser("decrypt", help="Decrypt a file")
    p_dec.add_argument("--input",  required=True, help="Path to encrypted file (.enc)")
    p_dec.add_argument("--output", required=True, help="Path for decrypted output")
    p_dec.add_argument("--key",    required=True, help="Path to RSA private key")

    # verify
    p_ver = sub.add_parser("verify", help="Verify file integrity (HMAC check)")
    p_ver.add_argument("--input", required=True, help="Path to encrypted file")
    p_ver.add_argument("--key",   required=True, help="Path to RSA private key")

    return parser


def main():
    _banner()
    parser = build_parser()
    args   = parser.parse_args()

    handlers = {
        "keygen" : cmd_keygen,
        "encrypt": cmd_encrypt,
        "decrypt": cmd_decrypt,
        "verify" : cmd_verify,
    }

    if args.command not in handlers:
        parser.print_help()
        sys.exit(0)

    handlers[args.command](args)


if __name__ == "__main__":
    main()
