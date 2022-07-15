# -*- mode: python -*-
# Compile using `pyinstaller SHARPpy-osx.spec --onefile --noconsole`
import sys
import glob
import sharppy
from sharppy._version import get_versions

print("PATH TO SHARPPY:", sharppy.__file__)
# Write the versions file using versioneer, because PyInstaller doesn't do this automatically
ver = get_versions()
ver = str(ver)
ver_fname = os.path.dirname(sharppy.__file__) + '/_version.py'
ver_file = open(ver_fname, 'w')
ver_file.write('def get_versions():\n')
ver_file.write('    return ' + ver)
ver_file.close()

del sharppy
import sharppy

# Get the working path for Azure-Pipelines build
runsharp_path = os.path.dirname(sharppy.__file__) + '/..'

# Analyze the SHARPpy package to get dependencies, etc.
a = Analysis(['SHARPpy.py'],
             pathex=[runsharp_path, runsharp_path+r'/runsharp'],
             hiddenimports=['xml.etree.ElementTree', 'sharppy.io.pecan_decoder', 'sharppy.io.spc_decoder', 'sharppy.io.buf_decoder', 'sharppy.io.uwyo_decoder', 'datasources.available', 'sharppy.sharptab.prof_collection', 'pkg_resources.py2_warn'],
             hookspath=None,
             runtime_hooks=None)
a.binaries = [x for x in a.binaries if not x[0].startswith("scipy")]

a.datas += [("sharppy/databases/PW-mean-inches.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases/PW-mean-inches.txt"), "DATA")]
a.datas += [("sharppy/databases/PW-stdev-inches.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases/PW-stdev-inches.txt"), "DATA")]
a.datas += [("sharppy/databases/sars_hail.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases/sars_hail.txt"), "DATA")]
a.datas += [("sharppy/databases/sars_supercell.txt", os.path.join(os.path.dirname(sharppy.__file__), "databases/sars_supercell.txt"), "DATA")]

sars_hail = glob.glob(os.path.join(os.path.dirname(sharppy.__file__), "databases/sars/hail/") + "*")
sars_supr = glob.glob(os.path.join(os.path.dirname(sharppy.__file__), "databases/sars/supercell/") + "*")
shapefiles = glob.glob(os.path.join(os.path.dirname(sharppy.__file__), "databases/shapefiles/") + "*")
datasources = glob.glob("../datasources/*.csv") + glob.glob("../datasources/*.xml")
rc_files = glob.glob(os.path.join(os.path.dirname(sharppy.__file__), "../rc/") + "*.png")

for hail in sars_hail:
    a.datas += [("sharppy/databases/sars/hail/" + hail.split("/")[-1], hail, "DATA")]
for supr in sars_supr:
    a.datas += [("sharppy/databases/sars/supercell/" + supr.split("/")[-1], supr, "DATA")]

for sf in shapefiles:
    a.datas += [("sharppy/databases/shapefiles/" + sf.split("/")[-1], sf, "DATA")]
for rc in rc_files:
    a.datas += [("rc/" + rc.split("/")[-1], rc, "DATA")]

for ds in datasources:
    if "__pycache__" in ds:
        continue
    a.datas += [("sharppy/datasources/" + ds.split("/")[-1], ds, "DATA")]

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SHARPpy',
          debug=True,
          strip=None,
          upx=True,
          console=False )

app = BUNDLE(exe,
             name='SHARPpy.app',
             icon='icons/SHARPpy.icns',
             info_plist={
                    'NSPrincipalClass': 'NSApplication',
                    'NSHighResolutionCapable': 'True',
                },
            )

# Revert the _version.py file to its original version using git
import subprocess
subprocess.Popen(['git', 'checkout', '--', ver_fname])
