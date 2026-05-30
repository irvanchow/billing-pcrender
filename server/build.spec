# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

_datas = [('../shared', 'shared')]
if os.path.isdir('assets') and any(f for f in os.listdir('assets') if not f.startswith('.')):
    _datas.append(('assets', 'assets'))
if os.path.isdir('data') and any(f for f in os.listdir('data') if not f.startswith('.')):
    _datas.append(('data', 'data'))

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('..'), os.path.abspath('.')],
    binaries=[],
    datas=_datas,
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'anyio',
        'anyio._backends._asyncio',
        'fastapi',
        'fastapi.responses',
        'starlette.routing',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'email.mime.text',
        'email.mime.multipart',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

_icon = 'assets/icon.ico' if os.path.isfile('assets/icon.ico') else None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RentalServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RentalServer',
)
