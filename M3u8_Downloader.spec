# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['M3u8_Downloader.py'],
    pathex=[],
    binaries=[],
    datas=[('videos.db', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='M3u8_Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
app = BUNDLE(
    exe,
    name='M3u8_Downloader.app',
    icon='icon.ico',
    bundle_identifier=None,
)
