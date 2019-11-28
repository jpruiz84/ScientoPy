# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['ScientoPyGui.py'],
             pathex=['C:\\Users\\user\\Desktop\\ScientoPy'],
             binaries=[],
             datas=[('wordcloudFiles/*', './wordcloud'),
                    ('Manual/*', './Manual'), 
                    ('dataInExample/*', './dataInExample'),
                    ('latexExample/*', './latexExample'),
                    ('scientopy_icon.ico', '.'), 
                    ('scientopy_icon.png', '.'), 
                    ('scientopy_logo.png', '.')],
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
          name='ScientoPyGui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='scientopy_icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ScientoPyGui')
