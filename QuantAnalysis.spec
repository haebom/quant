# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all required packages
datas = []
binaries = []
hiddenimports = []
packages = ['pandas', 'numpy', 'flask', 'binance', 'ta', 'plotly']
for package in packages:
    tmp_ret = collect_all(package)
    datas.extend(tmp_ret[0])
    binaries.extend(tmp_ret[1])
    hiddenimports.extend(tmp_ret[2])

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas + [
        ('templates', 'templates'),
        ('static', 'static'),
        ('assets', 'assets'),
        ('locales', 'locales'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['macos_runtime_hook.py'],
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
    [],
    exclude_binaries=True,
    name='QuantAnalysis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='arm64' if sys.platform == 'darwin' else None,
    codesign_identity='Developer ID Application:' if sys.platform == 'darwin' else None,
    entitlements_file='entitlements.plist',
    icon='assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QuantAnalysis'
)

# Add macOS specific bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='QuantAnalysis.app',
        icon='assets/icon.ico',
        bundle_identifier='com.haebom.quantanalysis',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'NSRequiresAquaSystemAppearance': 'False',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'LSMinimumSystemVersion': '10.13.0',
            'NSAppleEventsUsageDescription': 'This app requires access to run Python scripts.',
            'NSAppleScriptEnabled': False,
        }
    )
