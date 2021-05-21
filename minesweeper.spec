# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


added_files = [
    ('README.md', '.'),
    ('textures', 'textures'),
    ('audio', 'audio')
    ]


a = Analysis(['minesweeper.py'],
             pathex=['C:\\Users\\maxim\\PycharmProjects\\NSI-Minesweeper'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='minesweeper',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='textures\\game_icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='minesweeper')
