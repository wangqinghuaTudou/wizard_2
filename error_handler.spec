# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['error_handler.py'],
             pathex=['D:\\SCRIPT\\Wizard_2'],
             binaries=[],
             datas=[],
             hiddenimports=['PyQt5.QtPrintSupport'],
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
          name='error_handler',
          debug=False,
          bootloader_ignore_signals=True,
          strip=False,
          upx=True,
          console=False,
          version = 'compile\\version.rc',
          icon="D:\\SCRIPT\\Wizard_2\\ressources\\icons\\wizard_icon.ico")
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='error_handler')
