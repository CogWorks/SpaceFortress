from bbfreeze import Freezer
import shutil, glob, os, subprocess

includes = []
excludes = ['Tkinter', 'readline']

freezer = Freezer('dist/freeze/Config_Editor', includes=includes, excludes=excludes)
freezer.addScript('src/configeditor.py', gui_only=True)
freezer.include_py = False
freezer.use_compression = True
freezer()

os.chdir(freezer.distdir)

pyside_libs = []
for f in glob.glob("/usr/lib/libpyside-*") + glob.glob("/usr/lib/libshiboken-*"):
    lib = os.path.split(f)[1]
    shutil.copy(f, lib)
    pyside_libs.append(lib)
    
pyside_libs += glob.glob("PySide.Qt*.so")
for f in pyside_libs:
    output = subprocess.Popen(['otool', '-XL', f], stdout=subprocess.PIPE).communicate()[0]
    for line in output.splitlines():
        libpath = line.strip().split(" ")[0]
        if libpath != f and libpath[0] != "/" and libpath[0] != "@":
            subprocess.Popen(['install_name_tool', '-change', libpath, "@executable_path/"+libpath, f])
    