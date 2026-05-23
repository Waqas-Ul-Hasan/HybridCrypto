"""
app.py
======
Secure File Encryption System — PyQt6 Desktop Application
Clean, minimal dark UI — space-based layout, no border clutter.

Run:  python app.py
Build: pyinstaller HybridCrypto.spec
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
import hybrid_crypto as hc

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QTextEdit,
    QFrame, QStackedWidget, QProgressBar, QSizePolicy,
    QScrollArea, QComboBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QCursor, QLinearGradient, QPainter, QBrush
)

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN TOKENS — clean, minimal palette
# ─────────────────────────────────────────────────────────────────────────────
BG          = "#0A0C10"      # Main background — very dark
BG_SURFACE  = "#111318"      # Surface (slightly lighter)
BG_RAISED   = "#16191F"      # Raised elements
BG_INPUT    = "#1C2028"      # Input fields
BG_HOVER    = "#20242C"      # Hover state

ACCENT      = "#4F8EF7"      # Blue
GREEN       = "#34C759"      # Green
AMBER       = "#F5A623"      # Amber
RED         = "#FF453A"      # Red
PURPLE      = "#AF87FA"      # Purple

TEXT        = "#EAECF0"      # Primary text
TEXT_SUB    = "#6B7280"      # Subtle / muted text
TEXT_DIM    = "#9CA3AF"      # Dimmed

BORDER_SUB  = "#1E222A"      # Very subtle border (almost invisible)

FONT_UI     = "Segoe UI"
FONT_MONO   = "Consolas"


# ─────────────────────────────────────────────────────────────────────────────
#  WORKER
# ─────────────────────────────────────────────────────────────────────────────
class CryptoWorker(QObject):
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn, self._args, self._kwargs = fn, args, kwargs

    def run(self):
        try:
            self.finished.emit(self._fn(*self._args, **self._kwargs))
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  BASE COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def label(text, size=10, color=TEXT, bold=False, parent=None):
    l = QLabel(text, parent)
    l.setFont(QFont(FONT_UI, size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color}; background:transparent;")
    l.setWordWrap(True)
    return l


class PillButton(QPushButton):
    """Full pill-shaped primary button."""
    def __init__(self, text, bg=ACCENT, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont(FONT_UI, 10, QFont.Weight.Bold))
        self.setFixedHeight(44)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        r, g, b = int(bg[1:3],16), int(bg[3:5],16), int(bg[5:7],16)
        dark = f"#{max(0,r-35):02x}{max(0,g-35):02x}{max(0,b-35):02x}"
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: #fff;
                border: none;
                border-radius: 22px;
                padding: 0 28px;
            }}
            QPushButton:hover   {{ background: {dark}; }}
            QPushButton:pressed {{ background: {BG_INPUT}; color: {bg}; border: 1.5px solid {bg}; }}
            QPushButton:disabled{{ background: {BG_INPUT}; color: {TEXT_SUB}; }}
        """)


class GhostButton(QPushButton):
    """Subtle icon/text button."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont(FONT_UI, 9))
        self.setFixedHeight(32)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SUB};
                border: 1px solid {BORDER_SUB};
                border-radius: 8px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: {BG_HOVER};
                color: {TEXT};
                border-color: #2a3040;
            }}
        """)


class InputField(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFont(QFont(FONT_MONO, 9))
        self.setFixedHeight(42)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_INPUT};
                border: none;
                border-radius: 10px;
                padding: 0 16px;
                color: {TEXT};
                selection-background-color: {ACCENT};
            }}
            QLineEdit:focus {{
                background: #1e2330;
                outline: none;
            }}
            QLineEdit::placeholder {{ color: {TEXT_SUB}; }}
        """)


class FieldRow(QWidget):
    """Label + input + optional browse button — clean, no box."""
    def __init__(self, title, placeholder="", mode="open", filt="All Files (*.*)", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        self._mode, self._filt = mode, filt
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        lbl = label(title, size=9, color=TEXT_SUB)
        v.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.inp = InputField(placeholder)
        browse = GhostButton("Browse")
        browse.setFixedWidth(76)
        browse.clicked.connect(self._browse)
        row.addWidget(self.inp)
        row.addWidget(browse)
        v.addLayout(row)

    def _browse(self):
        if self._mode == "save":
            p, _ = QFileDialog.getSaveFileName(self, "Save As", "", self._filt)
        else:
            p, _ = QFileDialog.getOpenFileName(self, "Open", "", self._filt)
        if p:
            self.inp.setText(p)

    def value(self): return self.inp.text().strip()
    def setValue(self, v): self.inp.setText(v)


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background: {BORDER_SUB}; border: none;")


class LogPanel(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont(FONT_MONO, 9))
        self.setFixedHeight(150)
        self.setStyleSheet(f"""
            QTextEdit {{
                background: {BG};
                color: {TEXT_DIM};
                border: none;
                padding: 12px 16px;
            }}
        """)

    def _append(self, msg, color):
        self.append(f'<span style="color:{color}; font-family:Consolas; font-size:9pt;">{msg}</span>')
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def ok(self, m):   self._append(f"  {m}", GREEN)
    def err(self, m):  self._append(f"  {m}", RED)
    def info(self, m): self._append(f"  {m}", ACCENT)
    def kv(self, k, v):
        self._append(
            f'  <span style="color:{TEXT_SUB};">{k:<24}</span>'
            f'<span style="color:{TEXT_DIM};">{v}</span>', TEXT_DIM)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE BASE
# ─────────────────────────────────────────────────────────────────────────────
class BasePage(QWidget):
    def __init__(self, log: LogPanel, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{BG_SURFACE};")
        self.log = log
        self._thread = self._worker = None

    def _run(self, fn, *args, on_done=None, on_err=None, **kwargs):
        self._thread = QThread()
        self._worker = CryptoWorker(fn, *args, **kwargs)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        if on_done: self._worker.finished.connect(on_done)
        if on_err:  self._worker.error.connect(on_err)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _page_layout(self):
        """Returns a scrollable VBox layout for the page content."""
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background:{BG_SURFACE}; border:none;")
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG_SURFACE};")
        vbox = QVBoxLayout(inner)
        vbox.setContentsMargins(40, 36, 40, 36)
        vbox.setSpacing(0)
        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(scroll)
        return vbox

    def _heading(self, icon, title, subtitle, layout):
        row = QHBoxLayout()
        row.setSpacing(14)
        ico = label(icon, size=28)
        ico.setFixedWidth(44)
        tv = QVBoxLayout()
        tv.setSpacing(2)
        tv.addWidget(label(title, size=20, bold=True))
        tv.addWidget(label(subtitle, size=10, color=TEXT_SUB))
        row.addWidget(ico)
        row.addLayout(tv)
        row.addStretch()
        layout.addLayout(row)
        layout.addSpacing(32)

    def _section_label(self, text, layout):
        layout.addSpacing(24)
        lbl = label(text.upper(), size=8, color=TEXT_SUB, bold=True)
        lbl.setStyleSheet(f"color:{TEXT_SUB}; letter-spacing:1.5px; background:transparent;")
        layout.addWidget(lbl)
        layout.addSpacing(10)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────────────────────────────────────

class DashboardPage(BasePage):
    def __init__(self, log, parent=None):
        super().__init__(log, parent)
        layout = self._page_layout()

        # Hero
        hero = QWidget()
        hero.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0F1729, stop:1 #0A0C10);
            border-radius: 16px;
        """)
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(32, 32, 32, 32)
        hl.setSpacing(10)
        hl.addWidget(label("🔐", size=40))
        hl.addSpacing(4)
        hl.addWidget(label("Hybrid Crypto", size=28, bold=True))
        hl.addWidget(label("Secure File Encryption System", size=12, color=TEXT_SUB))
        hl.addSpacing(16)
        # tag row
        tags = QHBoxLayout()
        tags.setSpacing(8)
        for txt, col in [("RSA-2048", ACCENT), ("AES-256-CBC", AMBER), ("HMAC-SHA256", GREEN)]:
            t = QLabel(txt)
            t.setFont(QFont(FONT_MONO, 8))
            t.setStyleSheet(f"color:{col}; background:#ffffff0d; border-radius:6px; padding:4px 10px;")
            tags.addWidget(t)
        tags.addStretch()
        hl.addLayout(tags)
        layout.addWidget(hero)
        layout.addSpacing(28)

        # Dynamic Stats Row
        self._section_label("system status", layout)
        stats = QHBoxLayout()
        stats.setSpacing(12)
        
        self.lbl_keys = label("", size=14, bold=True)
        self.lbl_enc = label("", size=14, bold=True)
        lbl_backend = label(hc.CRYPTO_BACKEND, size=14, bold=True)
        lbl_backend.setStyleSheet(f"color:{AMBER}; background:transparent;")
        lbl_sec = label("AES-256 + RSA", size=14, bold=True)
        lbl_sec.setStyleSheet(f"color:{PURPLE}; background:transparent;")
        
        for title, lbl in [
            ("Key Pair Status", self.lbl_keys),
            ("Encrypted Files", self.lbl_enc),
            ("Crypto Engine", lbl_backend),
            ("Security Level", lbl_sec)
        ]:
            c = QWidget()
            c.setStyleSheet(f"background:{BG_RAISED}; border-radius:12px;")
            cl = QVBoxLayout(c)
            cl.setContentsMargins(18, 16, 18, 16)
            cl.setSpacing(6)
            cl.addWidget(label(title, size=9, color=TEXT_SUB))
            cl.addWidget(lbl)
            stats.addWidget(c)
            
        layout.addLayout(stats)
        layout.addSpacing(28)
        self._refresh_stats()

    def showEvent(self, event):
        self._refresh_stats()
        super().showEvent(event)
        
    def _refresh_stats(self):
        # Update dynamic stats when dashboard is shown
        keys_ok = Path("keys/private.pem").exists() and Path("keys/public.pem").exists()
        if keys_ok:
            self.lbl_keys.setText("Ready (Found)")
            self.lbl_keys.setStyleSheet(f"color:{GREEN}; background:transparent;")
        else:
            self.lbl_keys.setText("Missing")
            self.lbl_keys.setStyleSheet(f"color:{RED}; background:transparent;")
            
        enc_count = len(list(Path("samples").glob("*.enc"))) if Path("samples").exists() else 0
        self.lbl_enc.setText(f"{enc_count} files in /samples")
        self.lbl_enc.setStyleSheet(f"color:{ACCENT}; background:transparent;")

        # 3 algorithm cards — NO borders, background only
        self._section_label("how it works", layout)
        grid = QHBoxLayout()
        grid.setSpacing(12)
        for icon, name, desc, col in [
            ("⚡", "AES-256-CBC",    "Encrypts your file fast.\nSymmetric cipher, CBC mode.", AMBER),
            ("🔑", "RSA-2048",       "Protects the AES key.\nOnly your private key decrypts.", ACCENT),
            ("🛡️", "HMAC-SHA256",   "Detects tampering.\nVerified before decryption.", GREEN),
        ]:
            card = QWidget()
            card.setStyleSheet(f"background:{BG_RAISED}; border-radius:14px;")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 20, 20, 20)
            cl.setSpacing(8)
            cl.addWidget(label(icon, size=22))
            n = label(name, size=11, bold=True)
            n.setStyleSheet(f"color:{col}; background:transparent;")
            cl.addWidget(n)
            cl.addWidget(label(desc, size=9, color=TEXT_SUB))
            grid.addWidget(card)
        layout.addLayout(grid)
        layout.addSpacing(28)

        # Flow
        self._section_label("encryption flow", layout)
        flow = QWidget()
        flow.setStyleSheet(f"background:{BG_RAISED}; border-radius:14px;")
        fl = QVBoxLayout(flow)
        fl.setContentsMargins(24, 20, 24, 20)
        fl.setSpacing(0)
        steps = [
            ("1.", "Generate random AES-256 key & 128-bit IV", ACCENT),
            ("2.", "Encrypt file with AES-256-CBC  →  Ciphertext", AMBER),
            ("3.", "Compute HMAC-SHA256 over IV + Ciphertext", GREEN),
            ("4.", "Encrypt AES session key with RSA public key", PURPLE),
            ("5.", "Bundle components into secure .enc file", RED)
        ]
        for num, txt, col in steps:
            w = QWidget()
            w.setStyleSheet(f"background:{BG_SURFACE}; border-left:3px solid {col}; border-radius:6px;")
            wl = QHBoxLayout(w)
            wl.setContentsMargins(16, 12, 16, 12)
            wl.addWidget(label(num, size=11, bold=True, color=col))
            wl.addSpacing(6)
            wl.addWidget(label(txt, size=10, color=TEXT))
            wl.addStretch()
            fl.addWidget(w)
            if num != "5.": fl.addSpacing(8)
        layout.addWidget(flow)

        layout.addStretch()


class KeygenPage(BasePage):
    def __init__(self, log, parent=None):
        super().__init__(log, parent)
        layout = self._page_layout()
        self._heading("🔑", "Key Generation", "Create an RSA public/private key pair", layout)

        self.priv = FieldRow("Private Key  —  keep this secret", "keys/private.pem", "save", "PEM Files (*.pem)")
        self.priv.setValue("keys/private.pem")
        self.pub  = FieldRow("Public Key  —  share this freely", "keys/public.pem",  "save", "PEM Files (*.pem)")
        self.pub.setValue("keys/public.pem")
        layout.addWidget(self.priv)
        layout.addSpacing(16)
        layout.addWidget(self.pub)
        layout.addSpacing(24)

        # Key size selector
        self._section_label("key strength", layout)
        size_row = QHBoxLayout()
        size_row.setSpacing(10)
        self._size_btns = []
        for bits, lbl_txt, note in [
            (1024, "1024-bit", "Fast / Weak"),
            (2048, "2048-bit", "Recommended"),
            (4096, "4096-bit", "Strong / Slow"),
        ]:
            btn = QPushButton(f"{lbl_txt}\n{note}")
            btn.setCheckable(True)
            btn.setFixedSize(130, 58)
            btn.setFont(QFont(FONT_UI, 9))
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn._bits = bits
            btn.clicked.connect(lambda _, b=btn: self._select_size(b))
            self._apply_size_style(btn, False)
            size_row.addWidget(btn)
            self._size_btns.append(btn)
        size_row.addStretch()
        layout.addLayout(size_row)
        self._select_size(self._size_btns[1])  # default 2048

        layout.addSpacing(32)
        self.btn = PillButton("  Generate Key Pair", ACCENT)
        self.btn.setFixedWidth(220)
        self.btn.clicked.connect(self._go)
        layout.addWidget(self.btn)

        # Info note
        layout.addSpacing(28)
        note_w = QWidget()
        note_w.setStyleSheet(f"background:{BG_RAISED}; border-radius:12px;")
        nl = QHBoxLayout(note_w)
        nl.setContentsMargins(18, 14, 18, 14)
        nl.addWidget(label("ℹ", size=13, color=ACCENT))
        nl.addSpacing(10)
        nl.addWidget(label(
            "Your private key never leaves this machine. The public key can be freely "
            "shared — anyone with it can encrypt files that only you can decrypt.",
            size=9, color=TEXT_SUB
        ))
        layout.addWidget(note_w)
        layout.addStretch()

    def _apply_size_style(self, btn, active):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_INPUT};
                    color: {ACCENT};
                    border: 1.5px solid {ACCENT};
                    border-radius: 12px;
                    padding: 6px;
                    font-weight: bold;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_RAISED};
                    color: {TEXT_SUB};
                    border: none;
                    border-radius: 12px;
                    padding: 6px;
                }}
                QPushButton:hover {{ background:{BG_HOVER}; color:{TEXT}; }}
            """)

    def _select_size(self, selected):
        self._selected_bits = selected._bits
        for b in self._size_btns:
            self._apply_size_style(b, b is selected)

    def _go(self):
        priv, pub = self.priv.value(), self.pub.value()
        if not priv or not pub:
            self.log.err("Specify both key paths first."); return
        self.btn.setEnabled(False)
        self.log.info(f"Generating RSA-{self._selected_bits} key pair...")

        def done(m):
            self.log.ok("Key pair generated")
            for k, v in m.items(): self.log.kv(k, str(v))
            self.btn.setEnabled(True)

        def err(e):
            self.log.err(e); self.btn.setEnabled(True)

        self._run(hc.save_keypair, priv, pub, bits=self._selected_bits, on_done=done, on_err=err)


class EncryptPage(BasePage):
    def __init__(self, log, parent=None):
        super().__init__(log, parent)
        layout = self._page_layout()
        self._heading("🔒", "Encrypt File", "Encrypt any file with the recipient's public key", layout)

        self.inp = FieldRow("Input file", "Choose the file to encrypt", "open")
        self.out = FieldRow("Output file  (.enc)", "Where to save the encrypted file", "save", "Encrypted Files (*.enc)")
        self.key = FieldRow("Recipient's public key", "RSA public key (.pem)", "open", "PEM Files (*.pem)")
        self.key.setValue("keys/public.pem")
        for w in [self.inp, self.out, self.key]:
            layout.addWidget(w)
            layout.addSpacing(14)

        layout.addSpacing(20)

        # Progress bar — thin, accent colored, hidden by default
        self.prog = QProgressBar()
        self.prog.setRange(0, 0)
        self.prog.setFixedHeight(3)
        self.prog.hide()
        self.prog.setStyleSheet(f"""
            QProgressBar {{ background:{BG_INPUT}; border:none; border-radius:2px; }}
            QProgressBar::chunk {{ background:{AMBER}; border-radius:2px; }}
        """)
        layout.addWidget(self.prog)
        layout.addSpacing(8)

        self.btn = PillButton("  Encrypt", AMBER)
        self.btn.setFixedWidth(160)
        self.btn.clicked.connect(self._go)
        layout.addWidget(self.btn)
        layout.addStretch()

    def _go(self):
        inp, out, key = self.inp.value(), self.out.value(), self.key.value()
        if not all([inp, out, key]): self.log.err("Fill in all fields."); return
        if not Path(inp).exists(): self.log.err(f"File not found: {inp}"); return
        if not Path(key).exists(): self.log.err(f"Key not found: {key}"); return
        self.btn.setEnabled(False); self.prog.show()
        self.log.info(f"Encrypting  {Path(inp).name} ...")

        def done(m):
            self.prog.hide()
            self.log.ok(f"Done  —  {m['encrypted_size']} bytes  |  SHA-256: {m['original_hash'][:24]}...")
            for k, v in m.items(): self.log.kv(k, str(v))
            self.btn.setEnabled(True)

        def err(e):
            self.prog.hide(); self.log.err(e); self.btn.setEnabled(True)

        self._run(hc.encrypt_file, inp, out, key, on_done=done, on_err=err)


class DecryptPage(BasePage):
    def __init__(self, log, parent=None):
        super().__init__(log, parent)
        layout = self._page_layout()
        self._heading("🔓", "Decrypt File", "Decrypt a .enc file using your private key", layout)

        self.inp = FieldRow("Encrypted file  (.enc)", "Choose .enc file", "open", "Encrypted Files (*.enc)")
        self.out = FieldRow("Output file", "Where to save the decrypted file", "save")
        self.key = FieldRow("Your private key", "RSA private key (.pem)", "open", "PEM Files (*.pem)")
        self.key.setValue("keys/private.pem")
        for w in [self.inp, self.out, self.key]:
            layout.addWidget(w)
            layout.addSpacing(14)

        layout.addSpacing(20)
        self.prog = QProgressBar()
        self.prog.setRange(0, 0)
        self.prog.setFixedHeight(3)
        self.prog.hide()
        self.prog.setStyleSheet(f"""
            QProgressBar {{ background:{BG_INPUT}; border:none; border-radius:2px; }}
            QProgressBar::chunk {{ background:{GREEN}; border-radius:2px; }}
        """)
        layout.addWidget(self.prog)
        layout.addSpacing(8)

        self.btn = PillButton("  Decrypt", GREEN)
        self.btn.setFixedWidth(160)
        self.btn.clicked.connect(self._go)
        layout.addWidget(self.btn)
        layout.addStretch()

    def _go(self):
        inp, out, key = self.inp.value(), self.out.value(), self.key.value()
        if not all([inp, out, key]): self.log.err("Fill in all fields."); return
        if not Path(inp).exists(): self.log.err(f"File not found: {inp}"); return
        if not Path(key).exists(): self.log.err(f"Key not found: {key}"); return
        self.btn.setEnabled(False); self.prog.show()
        self.log.info(f"Decrypting  {Path(inp).name} ...")

        def done(m):
            self.prog.hide()
            self.log.ok(f"Decrypted  —  integrity {m['integrity']}")
            for k, v in m.items(): self.log.kv(k, str(v))
            self.btn.setEnabled(True)

        def err(e):
            self.prog.hide()
            msg = "INTEGRITY CHECK FAILED — file has been tampered with!" if "INTEGRITY" in e else e
            self.log.err(msg); self.btn.setEnabled(True)

        self._run(hc.decrypt_file, inp, out, key, on_done=done, on_err=err)


class VerifyPage(BasePage):
    def __init__(self, log, parent=None):
        super().__init__(log, parent)
        layout = self._page_layout()
        self._heading("✅", "Verify Integrity", "Check if an encrypted file has been tampered with", layout)

        self.inp = FieldRow("Encrypted file  (.enc)", "Choose .enc file", "open", "Encrypted Files (*.enc)")
        self.key = FieldRow("Your private key", "RSA private key (.pem)", "open", "PEM Files (*.pem)")
        self.key.setValue("keys/private.pem")
        for w in [self.inp, self.key]:
            layout.addWidget(w)
            layout.addSpacing(14)

        layout.addSpacing(20)
        self.btn = PillButton("  Verify", PURPLE)
        self.btn.setFixedWidth(160)
        self.btn.clicked.connect(self._go)
        layout.addWidget(self.btn)

        # Result — large, clean status badge
        layout.addSpacing(24)
        self.badge = QLabel("")
        self.badge.setFixedHeight(60)
        self.badge.setFont(QFont(FONT_UI, 12, QFont.Weight.Bold))
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setStyleSheet("background:transparent;")
        layout.addWidget(self.badge)
        layout.addStretch()

    def _go(self):
        inp, key = self.inp.value(), self.key.value()
        if not all([inp, key]): self.log.err("Fill in all fields."); return
        self.btn.setEnabled(False)
        self.badge.setText("Checking...")
        self.badge.setStyleSheet(f"color:{TEXT_SUB}; background:transparent;")
        self.log.info(f"Verifying  {Path(inp).name} ...")

        def done(r):
            ok = "VERIFIED" in r["integrity"]
            if ok:
                self.badge.setText("  Integrity Verified")
                self.badge.setStyleSheet(f"""
                    color:{GREEN}; background:#0A2A18;
                    border-radius:14px; font-weight:bold; font-size:13pt;
                """)
                self.log.ok("HMAC verified — file is authentic and unmodified")
            else:
                self.badge.setText("  Integrity Failed")
                self.badge.setStyleSheet(f"""
                    color:{RED}; background:#2A0A0A;
                    border-radius:14px; font-weight:bold; font-size:13pt;
                """)
                self.log.err("HMAC mismatch — file may have been tampered with")
            self.btn.setEnabled(True)

        def err(e):
            self.badge.setText("  Error")
            self.badge.setStyleSheet(f"color:{RED}; background:transparent;")
            self.log.err(e); self.btn.setEnabled(True)

        self._run(hc.verify_file_integrity, inp, key, on_done=done, on_err=err)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR BUTTON
# ─────────────────────────────────────────────────────────────────────────────
class NavBtn(QPushButton):
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self._icon, self._text = icon, text
        self.setCheckable(True)
        self.setFixedHeight(46)
        self.setFont(QFont(FONT_UI, 10))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setText(f"  {icon}   {text}")
        self._set(False)

    def _set(self, active):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_RAISED};
                    color: {TEXT};
                    border: none;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 14px;
                    font-weight: 600;
                    margin: 0 8px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SUB};
                    border: none;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 14px;
                    margin: 0 8px;
                }}
                QPushButton:hover {{
                    background: {BG_HOVER};
                    color: {TEXT_DIM};
                }}
            """)

    def setActive(self, v): self._set(v)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HybridCrypto — Secure File Encryption")
        self.setMinimumSize(960, 640)
        self.resize(1100, 720)

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(BG))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
        self.setPalette(pal)

        root = QWidget()
        root.setStyleSheet(f"background:{BG};")
        self.setCentralWidget(root)
        ml = QHBoxLayout(root)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background:{BG};")
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(2)

        # Logo
        logo = QWidget()
        logo.setFixedHeight(68)
        logo.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(logo)
        ll.setContentsMargins(22, 0, 16, 0)
        ico = QLabel("🔐")
        ico.setFont(QFont("Segoe UI Emoji", 20))
        ico.setStyleSheet("background:transparent;")
        ltxt = QVBoxLayout()
        ltxt.setSpacing(1)
        t1 = QLabel("HybridCrypto")
        t1.setFont(QFont(FONT_UI, 11, QFont.Weight.Bold))
        t1.setStyleSheet(f"color:{TEXT}; background:transparent;")
        t2 = QLabel("v1.0")
        t2.setFont(QFont(FONT_UI, 8))
        t2.setStyleSheet(f"color:{TEXT_SUB}; background:transparent;")
        ltxt.addWidget(t1); ltxt.addWidget(t2)
        ll.addWidget(ico); ll.addSpacing(8); ll.addLayout(ltxt)
        sb.addWidget(logo)
        sb.addSpacing(8)

        nav_items = [
            ("🏠", "Dashboard"),
            ("🔑", "Key Generation"),
            ("🔒", "Encrypt"),
            ("🔓", "Decrypt"),
            ("✅", "Verify"),
        ]
        self._nav_btns = []
        for icon, text in nav_items:
            btn = NavBtn(icon, text)
            btn.clicked.connect(lambda _, i=len(self._nav_btns): self._switch(i))
            sb.addWidget(btn)
            self._nav_btns.append(btn)

        sb.addStretch()

        # Bottom label
        ver = QLabel(f"Python {sys.version.split()[0]}\n{hc.CRYPTO_BACKEND}")
        ver.setFont(QFont(FONT_MONO, 7))
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet(f"color:{TEXT_SUB}; background:transparent; padding:12px;")
        sb.addWidget(ver)

        ml.addWidget(sidebar)

        # ── Right side ───────────────────────────────────────────────────────
        right = QWidget()
        right.setStyleSheet(f"background:{BG_SURFACE};")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # Shared log panel
        self.log_panel = LogPanel()

        # Pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{BG_SURFACE};")
        for PageClass in [DashboardPage, KeygenPage, EncryptPage, DecryptPage, VerifyPage]:
            self.stack.addWidget(PageClass(self.log_panel))
        rl.addWidget(self.stack, 1)

        # Log footer — borderless, just a background change
        log_bar = QWidget()
        log_bar.setStyleSheet(f"background:{BG};")
        lbl = QVBoxLayout(log_bar)
        lbl.setContentsMargins(0, 0, 0, 0)
        lbl.setSpacing(0)

        # Log header
        lhdr = QWidget()
        lhdr.setFixedHeight(36)
        lhdr.setStyleSheet(f"background:{BG};")
        lhdr_row = QHBoxLayout(lhdr)
        lhdr_row.setContentsMargins(20, 0, 16, 0)
        lhdr_row.addWidget(label("Output", size=8, color=TEXT_SUB, bold=True))
        lhdr_row.addStretch()
        clr = GhostButton("Clear")
        clr.setFixedSize(52, 24)
        clr.clicked.connect(self.log_panel.clear)
        lhdr_row.addWidget(clr)
        lbl.addWidget(lhdr)
        lbl.addWidget(self.log_panel)
        rl.addWidget(log_bar)

        ml.addWidget(right, 1)
        self._switch(0)
        self.log_panel.info("Ready")

    def _switch(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self._nav_btns):
            b.setActive(i == idx)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HybridCrypto")
    app.setFont(QFont(FONT_UI, 10))
    app.setStyleSheet(f"""
        QScrollBar:vertical {{
            background:{BG_SURFACE}; width:6px; border-radius:3px;
        }}
        QScrollBar::handle:vertical {{
            background:{BG_RAISED}; border-radius:3px; min-height:20px;
        }}
        QScrollBar::handle:vertical:hover {{ background:#2a303c; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        QScrollBar:horizontal {{ height:0; }}
        QToolTip {{
            background:{BG_RAISED}; color:{TEXT};
            border:1px solid {BORDER_SUB}; border-radius:6px; padding:4px 8px;
        }}
    """)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
