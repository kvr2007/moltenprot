# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['moltenprot/__main__.py'],
             binaries=[],
             datas=[('moltenprot/VERSION', 'moltenprot'), ('COPYING', 'moltenprot'), ('moltenprot/resources/report.template', 'moltenprot/resources')],
             hiddenimports=['scipy.special.cython_special'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['joblib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# add folder with demo files, based on this solution
# https://stackoverflow.com/questions/11322538/including-a-directory-using-pyinstaller
a.datas += Tree('moltenprot/demo_data', prefix='moltenprot/demo_data')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='moltenprot_mac',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='moltenprot/ui/icons/app_icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='moltenprot_mac')
app = BUNDLE(coll,
             name='moltenprot_mac.app',
             icon='moltenprot/ui/icons/app_icon.ico',
             bundle_identifier=None)
