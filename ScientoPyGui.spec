# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Icon is platform-dependent
if sys.platform == 'win32':
    icon_file = 'scientopy_icon.ico'
elif sys.platform == 'darwin':
    icon_file = 'scientopy_icon.png'
else:
    icon_file = 'scientopy_icon.png'

a = Analysis(
    ['ScientoPyGui.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('wordcloudFiles', 'wordcloud'),
        ('Manual/ScientoPyGui_user_manual.pdf', 'Manual'),
        ('Manual/ScientoPy_user_manual.pdf', 'Manual'),
        ('Manual/example_paper.pdf', 'Manual'),
        ('dataInExample', 'dataInExample'),
        ('latexExample', 'latexExample'),
        ('scientopy_icon.ico', '.'),
        ('scientopy_icon.png', '.'),
        ('scientopy_logo.png', '.'),
        # CLI scripts for advanced users
        ('scientoPy.py', '.'),
        ('preProcess.py', '.'),
        ('generateBibtex.py', '.'),
        ('ScientoPyClass.py', '.'),
        ('PreProcessClass.py', '.'),
        ('globalVar.py', '.'),
        ('graphUtils.py', '.'),
        ('paperUtils.py', '.'),
        ('paperSave.py', '.'),
    ],
    hiddenimports=[
        'scipy.spatial.transform._rotation_groups',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ScientoPyGui',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScientoPyGui',
)
