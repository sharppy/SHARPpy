# -*- mode: python -*-
import glob
import sharppy

block_cipher = None


a = Analysis(['SHARPget.py'],
             pathex=[r'C:\Users\nickr\workspace\SHARPpy\runsharp'],
             binaries=None,
             datas=[],
             hiddenimports=['xml.etree.ElementTree', 'sharppy.io.archive_decoder', 'datasources.available', 'sharppy.io.ibufr_decoder', 'sharppy.io.bufrpy', 'sharppy.io.spc_decoder', 'sharppy.io.buf_decoder', 'dateutil', 'six', 'sharppy.io.fsl_decoder'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

for b in a.binaries:
    if b[0] == '':
        a.binaries.remove(b)
            
a.datas += [("sharppy\\databases\\PW-mean-inches.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\PW-mean-inches.txt"), "DATA")]
a.datas += [("sharppy\\databases\\PW-stdev-inches.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\PW-stdev-inches.txt"), "DATA")]
a.datas += [("sharppy\\databases\\sars_hail.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\sars_hail.txt"), "DATA")]
a.datas += [("sharppy\\databases\\sars_supercell.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\sars_supercell.txt"), "DATA")]
a.datas += [("icons\\SHARPpy_imet.png", "icons\\SHARPpy_imet.png", "DATA")]
a.datas += [("icons\\SHARPget_imet.png", "icons\\SHARPget_imet.png", "DATA")]
#a.datas += [("sharppy\\io\\bufrpy\\b_table", os.path.join(os.path.dirname(sharppy.__file__), "io\\bufrpy\\b_table"), "DATA")]
#a.datas += [("sharppy\\io\\bufrpy\\d_table", os.path.join(os.path.dirname(sharppy.__file__), "io\\bufrpy\\d_table"), "DATA")]

sars_hail = glob.glob(os.path.join(os.path.dirname(sharppy.__file__), "databases\\sars\hail\\") + "*")
sars_supr = glob.glob(os.path.join(os.path.dirname(sharppy.__file__), "databases\\sars\supercell\\") + "*")
shapefiles = glob.glob(os.path.join(os.path.dirname(sharppy.__file__), "databases\\shapefiles\\") + "*")
datasources = glob.glob("..\\datasources\\" + "*")

for hail in sars_hail:
    a.datas += [("sharppy\\databases\\sars\\hail\\" + hail.split("\\")[-1], hail, "DATA")]
for supr in sars_supr:
    a.datas += [("sharppy\\databases\\sars\\supercell\\" + supr.split("\\")[-1], supr, "DATA")]

for sf in shapefiles:
    a.datas += [("sharppy\\databases\\shapefiles\\" + sf.split("\\")[-1], sf, "DATA")]

for ds in datasources:
    a.datas += [("sharppy\\datasources\\" + ds.split("\\")[-1], ds, "DATA")]

for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='SHARPpy',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='icons\\SHARPget_imet.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='SHARPget')