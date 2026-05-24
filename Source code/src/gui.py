"""
gui.py
======
Graphical User Interface for the Secure File Encryption System
Uses Python's built-in tkinter — no extra install required.

Run: python gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
from pathlib import Path

# Add src directory to path when running from project root
sys.path.insert(0, str(Path(__file__).parent))
import hybrid_crypto as hc

# ─────────────────────────────────────────────────────────────────────────────
#  Color Palette & Fonts
# ─────────────────────────────────────────────────────────────────────────────
BG_DARK      = "#0D1117"
BG_CARD      = "#161B22"
BG_INPUT     = "#21262D"
ACCENT_BLUE  = "#58A6FF"
ACCENT_GREEN = "#3FB950"
ACCENT_RED   = "#F85149"
ACCENT_AMBER = "#E3B341"
TEXT_PRIMARY = "#F0F6FC"
TEXT_MUTED   = "#8B949E"
BORDER       = "#30363D"

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_MONO   = ("Consolas", 9)

# ─────────────────────────────────────────────────────────────────────────────
#  Main Application
# ─────────────────────────────────────────────────────────────────────────────

class HybridCryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure File Encryption System — Hybrid Crypto")
        self.geometry("900x680")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # State variables
        self.input_var      = tk.StringVar()
        self.output_var     = tk.StringVar()
        self.pub_key_var    = tk.StringVar(value="keys/public.pem")
        self.priv_key_var   = tk.StringVar(value="keys/private.pem")
        self.priv_gen_var   = tk.StringVar(value="keys/private.pem")
        self.pub_gen_var    = tk.StringVar(value="keys/public.pem")
        self.bits_var       = tk.IntVar(value=2048)
        self.status_var     = tk.StringVar(value="Ready")

        self._build_ui()

    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(hdr, text="🔐", font=("Segoe UI Emoji", 28), bg=BG_DARK,
                 fg=ACCENT_BLUE).pack(side="left")
        tk.Label(hdr, text="Secure File Encryption System",
                 font=FONT_TITLE, bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left", padx=12)
        tk.Label(hdr, text="Hybrid RSA-2048 + AES-256-CBC",
                 font=FONT_NORMAL, bg=BG_DARK, fg=TEXT_MUTED).pack(side="right")

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", padx=24, pady=(0, 12))

        # Notebook tabs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",         background=BG_DARK,  borderwidth=0)
        style.configure("TNotebook.Tab",     background=BG_CARD,  foreground=TEXT_MUTED,
                        padding=[16, 8], font=FONT_NORMAL)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_INPUT)],
                  foreground=[("selected", ACCENT_BLUE)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=24, pady=0)

        self._tab_keygen(nb)
        self._tab_encrypt(nb)
        self._tab_decrypt(nb)
        self._tab_verify(nb)

        # Log area
        log_frame = tk.Frame(self, bg=BG_CARD, bd=0, highlightthickness=0)
        log_frame.pack(fill="both", padx=24, pady=(10, 0))

        tk.Label(log_frame, text="Output Log", font=FONT_HEAD,
                 bg=BG_CARD, fg=ACCENT_BLUE).pack(anchor="w", padx=12, pady=(8, 0))

        self.log = scrolledtext.ScrolledText(
            log_frame, height=7, bg=BG_DARK, fg=TEXT_PRIMARY,
            font=FONT_MONO, bd=0, relief="flat", wrap="word",
            insertbackground=ACCENT_BLUE
        )
        self.log.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        self.log.config(state="disabled")

        # Status bar
        sbar = tk.Frame(self, bg=BG_CARD, height=28)
        sbar.pack(fill="x", padx=24, pady=(0, 8))
        self.prog = ttk.Progressbar(sbar, mode="indeterminate", length=160)
        self.prog.pack(side="right", padx=(0, 12), pady=4)
        tk.Label(sbar, textvariable=self.status_var,
                 font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_MUTED).pack(side="left", padx=12, pady=4)

    # ──────────────────────────────────────────────────────────────────────────
    def _card(self, parent):
        f = tk.Frame(parent, bg=BG_CARD, bd=0)
        f.pack(fill="both", expand=True, padx=4, pady=4)
        return f

    def _field(self, parent, label, var, row, browse_cmd=None, hint=""):
        tk.Label(parent, text=label, font=FONT_NORMAL,
                 bg=BG_CARD, fg=TEXT_MUTED).grid(row=row, column=0, sticky="w",
                                                   padx=(16,8), pady=6)
        entry = tk.Entry(parent, textvariable=var, font=FONT_MONO,
                         bg=BG_INPUT, fg=TEXT_PRIMARY, bd=0, relief="flat",
                         insertbackground=ACCENT_BLUE, width=52)
        entry.grid(row=row, column=1, sticky="ew", padx=4, pady=6, ipady=5)
        if browse_cmd:
            tk.Button(parent, text="Browse", command=browse_cmd,
                      bg=BG_INPUT, fg=ACCENT_BLUE, bd=0, relief="flat",
                      font=FONT_NORMAL, padx=8, cursor="hand2").grid(
                          row=row, column=2, padx=(4,16), pady=6)
        if hint:
            tk.Label(parent, text=hint, font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_MUTED).grid(row=row+1, column=1, sticky="w", padx=4)
        parent.columnconfigure(1, weight=1)

    def _btn(self, parent, text, cmd, color=ACCENT_BLUE):
        b = tk.Button(parent, text=text, command=cmd, bg=color, fg="#FFFFFF",
                      font=FONT_HEAD, bd=0, relief="flat", padx=24, pady=10,
                      cursor="hand2", activebackground=color, activeforeground="#FFFFFF")
        b.pack(pady=(16, 8))
        return b

    # ──────────────────────────────────────────────────────────────────────────
    def _tab_keygen(self, nb):
        tab = tk.Frame(nb, bg=BG_CARD)
        nb.add(tab, text="  🔑 Key Generation  ")
        card = self._card(tab)

        tk.Label(card, text="Generate RSA Key Pair", font=FONT_HEAD,
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(row=0, columnspan=3, pady=(16,4), padx=16, sticky="w")
        tk.Label(card, text="Creates a 2048-bit RSA private/public key pair for asymmetric encryption.",
                 font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_MUTED).grid(
                     row=1, columnspan=3, padx=16, sticky="w")

        self._field(card, "Private Key Path", self.priv_gen_var, 2,
                    lambda: self._save_dialog(self.priv_gen_var, "PEM Files", "*.pem"))
        self._field(card, "Public Key Path",  self.pub_gen_var,  3,
                    lambda: self._save_dialog(self.pub_gen_var, "PEM Files", "*.pem"))

        # Key size radio
        rf = tk.Frame(card, bg=BG_CARD)
        rf.grid(row=4, column=0, columnspan=3, sticky="w", padx=16, pady=(4,0))
        tk.Label(rf, text="Key Size:", font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_MUTED).pack(side="left")
        for bits in [1024, 2048, 4096]:
            tk.Radiobutton(rf, text=f"{bits}-bit", variable=self.bits_var, value=bits,
                           bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
                           activebackground=BG_CARD, font=FONT_NORMAL).pack(side="left", padx=8)

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.grid(row=5, columnspan=3, pady=16)
        self._btn(btn_frame, "⚙  Generate Key Pair", self._do_keygen, ACCENT_BLUE)

    def _tab_encrypt(self, nb):
        tab = tk.Frame(nb, bg=BG_CARD)
        nb.add(tab, text="  🔒 Encrypt  ")
        card = self._card(tab)

        tk.Label(card, text="Encrypt a File", font=FONT_HEAD,
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(row=0, columnspan=3, pady=(16,4), padx=16, sticky="w")

        self._field(card, "Input File",    self.input_var,   1,
                    lambda: self._open_dialog(self.input_var))
        self._field(card, "Output File",   self.output_var,  2,
                    lambda: self._save_dialog(self.output_var, "Encrypted Files", "*.enc"))
        self._field(card, "Public Key",    self.pub_key_var, 3,
                    lambda: self._open_dialog(self.pub_key_var, "PEM Files", "*.pem"))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.grid(row=4, columnspan=3, pady=16)
        self._btn(btn_frame, "🔒  Encrypt File", self._do_encrypt, ACCENT_AMBER)

    def _tab_decrypt(self, nb):
        tab = tk.Frame(nb, bg=BG_CARD)
        nb.add(tab, text="  🔓 Decrypt  ")
        card = self._card(tab)

        tk.Label(card, text="Decrypt a File", font=FONT_HEAD,
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(row=0, columnspan=3, pady=(16,4), padx=16, sticky="w")

        self._field(card, "Encrypted File (.enc)", self.input_var,    1,
                    lambda: self._open_dialog(self.input_var, "ENC Files", "*.enc"))
        self._field(card, "Output File",           self.output_var,   2,
                    lambda: self._save_dialog(self.output_var, "All Files", "*.*"))
        self._field(card, "Private Key",           self.priv_key_var, 3,
                    lambda: self._open_dialog(self.priv_key_var, "PEM Files", "*.pem"))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.grid(row=4, columnspan=3, pady=16)
        self._btn(btn_frame, "🔓  Decrypt File", self._do_decrypt, ACCENT_GREEN)

    def _tab_verify(self, nb):
        tab = tk.Frame(nb, bg=BG_CARD)
        nb.add(tab, text="  ✅ Verify  ")
        card = self._card(tab)

        tk.Label(card, text="Verify File Integrity (HMAC-SHA256)", font=FONT_HEAD,
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(row=0, columnspan=3, pady=(16,4), padx=16, sticky="w")
        tk.Label(card, text="Checks if the encrypted file has been tampered with.",
                 font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_MUTED).grid(row=1, columnspan=3, padx=16, sticky="w")

        self._field(card, "Encrypted File", self.input_var,    2,
                    lambda: self._open_dialog(self.input_var, "ENC Files", "*.enc"))
        self._field(card, "Private Key",    self.priv_key_var, 3,
                    lambda: self._open_dialog(self.priv_key_var, "PEM Files", "*.pem"))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.grid(row=4, columnspan=3, pady=16)
        self._btn(btn_frame, "✅  Verify Integrity", self._do_verify, ACCENT_GREEN)

    # ──────────────────────────────────────────────────────────────────────────
    # File dialogs
    # ──────────────────────────────────────────────────────────────────────────

    def _open_dialog(self, var, fdesc="All Files", ftype="*.*"):
        path = filedialog.askopenfilename(filetypes=[(fdesc, ftype), ("All", "*.*")])
        if path:
            var.set(path)

    def _save_dialog(self, var, fdesc="All Files", ftype="*.*"):
        path = filedialog.asksaveasfilename(defaultextension=ftype.replace("*", ""),
                                            filetypes=[(fdesc, ftype), ("All", "*.*")])
        if path:
            var.set(path)

    # ──────────────────────────────────────────────────────────────────────────
    # Log helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _log(self, msg: str, color: str = TEXT_PRIMARY):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    # ──────────────────────────────────────────────────────────────────────────
    # Actions (run in background thread to keep UI responsive)
    # ──────────────────────────────────────────────────────────────────────────

    def _run_async(self, fn):
        self.prog.start(10)
        t = threading.Thread(target=fn, daemon=True)
        t.start()

    def _do_keygen(self):
        def task():
            self._set_status("Generating keys...")
            self._log("─" * 55)
            self._log("  Generating RSA key pair...")
            try:
                meta = hc.save_keypair(self.priv_gen_var.get(), self.pub_gen_var.get(), self.bits_var.get())
                for k, v in meta.items():
                    self._log(f"  {k:<20}: {v}")
                self._log("  ✔  Key pair generated successfully!")
                messagebox.showinfo("Success", f"Key pair saved!\n\nPrivate: {meta['private_key']}\nPublic:  {meta['public_key']}")
            except Exception as e:
                self._log(f"  ✘  Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self.prog.stop()
                self._set_status("Ready")
        self._run_async(task)

    def _do_encrypt(self):
        def task():
            self._set_status("Encrypting...")
            self._log("─" * 55)
            self._log(f"  Encrypting: {self.input_var.get()}")
            try:
                meta = hc.encrypt_file(self.input_var.get(), self.output_var.get(), self.pub_key_var.get())
                for k, v in meta.items():
                    self._log(f"  {k:<20}: {v}")
                self._log("  ✔  Encryption complete!")
                messagebox.showinfo("Success", f"File encrypted!\n\nOutput: {meta['output_file']}\nOriginal SHA-256:\n{meta['original_hash']}")
            except Exception as e:
                self._log(f"  ✘  Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self.prog.stop()
                self._set_status("Ready")
        self._run_async(task)

    def _do_decrypt(self):
        def task():
            self._set_status("Decrypting...")
            self._log("─" * 55)
            self._log(f"  Decrypting: {self.input_var.get()}")
            try:
                meta = hc.decrypt_file(self.input_var.get(), self.output_var.get(), self.priv_key_var.get())
                for k, v in meta.items():
                    self._log(f"  {k:<20}: {v}")
                self._log("  ✔  Decryption complete — integrity verified!")
                messagebox.showinfo("Success", f"File decrypted!\n\nOutput: {meta['output_file']}\nIntegrity: {meta['integrity']}")
            except ValueError as e:
                self._log(f"  ✘  {e}")
                messagebox.showerror("Integrity Failure", str(e))
            except Exception as e:
                self._log(f"  ✘  Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self.prog.stop()
                self._set_status("Ready")
        self._run_async(task)

    def _do_verify(self):
        def task():
            self._set_status("Verifying...")
            self._log("─" * 55)
            self._log(f"  Verifying: {self.input_var.get()}")
            result = hc.verify_file_integrity(self.input_var.get(), self.priv_key_var.get())
            self._log(f"  Integrity: {result['integrity']}")
            if "VERIFIED" in result["integrity"]:
                messagebox.showinfo("Integrity Check", f"✔  {result['integrity']}\n\nThe file has NOT been tampered with.")
            else:
                messagebox.showwarning("Integrity Check", f"✘  {result['integrity']}\n\nFile may have been tampered with!\n{result.get('error','')}")
            self.prog.stop()
            self._set_status("Ready")
        self._run_async(task)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = HybridCryptoApp()
    app.mainloop()
