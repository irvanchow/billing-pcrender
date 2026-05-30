# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

_datas = [('../shared', 'shared')]
if os.path.isdir('assets') and any(f for f in os.listdir('assets') if not f.startswith('.')):
    _datas.append(('assets', 'assets'))

_icon = 'assets/icon.ico' if os.path.isfile('assets/icon.ico') else None

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('..'), os.path.abspath('.')],
    binaries=[],
    datas=_datas,
    hiddenimports=[
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'pywintypes',
        'win32security',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='KioskTimer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    uac_admin=True,
    icon=_icon,
)
