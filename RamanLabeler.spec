# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['Ui_main.py', 'Ui_Manual_label.py',
    'models.py', 'utils.py', 'function.py', 'Plot_Raman.py',
     'Plot_Voigt.py', 'Plot_Data_generator.py'],
    pathex=[],
    binaries=[],
    datas=[('save_model/*', 'save_model')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RamanLabeler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # upx=True,
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
    a.datas,
    strip=False,
    # upx=True,
    # upx_exclude=[],
    name='RamanLabeler',
)
