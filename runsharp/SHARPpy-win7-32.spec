# -*- mode: python -*-
import glob
import sharppy
from sharppy._version import get_versions

# Write the versions file using versioneer, because PyInstaller doesn't do this automatically
ver = get_versions()
ver = str(ver)
ver_fname = os.path.dirname(sharppy.__file__) + '\\_version.py'
ver_file = open(ver_fname, 'w')
ver_file.write('def get_versions():\n')
ver_file.write('    return ' + ver)
ver_file.close()


a = Analysis(['SHARPpy.py'],
             pathex=[r'C:\Users\Tim\SHARPpy\runsharp'],
             hiddenimports=['xml.etree.ElementTree', 'sharppy.io.pecan_decoder', 'sharppy.io.spc_decoder', 'sharppy.io.buf_decoder', 'sharppy.io.uwyo_decoder', 'datasources.available', 'sharppy.sharptab.prof_collection'],
             hookspath=None,
             runtime_hooks=None)

for b in a.binaries:
    if b[0] == '':
        a.binaries.remove(b)
            
a.datas += [("sharppy\\databases\\PW-mean-inches.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\PW-mean-inches.txt"), "DATA")]
a.datas += [("sharppy\\databases\\PW-stdev-inches.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\PW-stdev-inches.txt"), "DATA")]
a.datas += [("sharppy\\databases\\sars_hail.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\sars_hail.txt"), "DATA")]
a.datas += [("sharppy\\databases\\sars_supercell.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases\\sars_supercell.txt"), "DATA")]

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
        
#print a.scripts
#print a.binaries
#print a.zipfiles
        
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SHARPpy.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False, 
          icon="icons\\SHARPpy.ico")

# Revert the _version.py file to its original version using git
import subprocess
subprocess.Popen(['git', 'checkout', '--', ver_fname])

