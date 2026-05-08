# -*- mode: python ; coding: utf-8 -*-
# PyInstaller — pakiet katalogowy (--onedir) pod Windows.
# Budowanie z korzenia repo:  pyinstaller SOKs_LOK.spec

import os

block_cipher = None

try:
    SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
except NameError:  # pragma: no cover
    SPEC_DIR = os.path.abspath('.')

code_entry = os.path.join(SPEC_DIR, 'Code', 'operator_ui_handler.py')

a = Analysis(
    [code_entry],
    pathex=[SPEC_DIR, os.path.join(SPEC_DIR, 'Code')],
    binaries=[],
    datas=[
        (os.path.join(SPEC_DIR, 'Ui_Files'), 'Ui_Files'),
        (os.path.join(SPEC_DIR, 'Resources'), 'Resources'),
    ],
    hiddenimports=[
        'PySide6.QtUiTools',
        'PySide6.QtXml',
        'Resources.resources_rc',
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
    [],
    exclude_binaries=True,
    name='SOKs_LOK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SOKs_LOK',
)
