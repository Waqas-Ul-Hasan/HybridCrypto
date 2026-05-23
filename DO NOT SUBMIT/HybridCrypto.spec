# HybridCrypto.spec
# PyInstaller spec file — build with: pyinstaller HybridCrypto.spec

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['.', 'src'],
    binaries=[],
    datas=[('src/*.py', 'src')],
    hiddenimports=[
        'Crypto.PublicKey.RSA',
        'Crypto.Cipher.AES',
        'Crypto.Cipher.PKCS1_OAEP',
        'Crypto.Hash.SHA256',
        'Crypto.Random',
        'Crypto.Util.Padding',
        'colorama',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HybridCrypto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No console window (windowed mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
