# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('Index', 'Index')],
    hiddenimports=[
        'pygame',
        'Index.World.level_1',
        'Index.World.procedural_levels',
        'Index.World.style_worlds',
        'Index.Player.player',
        'Index.Player.style_player',
        'Index.Enemies.enemie',
        'Index.Enemies.style_enemie',
        'Index.Menu.menu_system',
        'Index.Utils.collision_helper'
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
    name='MiJuego',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mantenemos esto en True para ver errores
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)