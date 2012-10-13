from bbfreeze import Freezer
import shutil, glob, os, sys, subprocess

def find_n_fix_missing(libs):
    missing = []
    for f in libs:
        output = subprocess.Popen(['otool', '-XL', f], stdout=subprocess.PIPE).communicate()[0]
        for line in output.splitlines():
            libpath = line.strip().split(" ")[0]
            if libpath != f and libpath[0] != "/" and libpath[0] != "@":
                if not libpath in missing and not '.framework' in libpath:
                    missing.append(libpath)
                    shutil.copy(os.path.join('/usr/lib', libpath), libpath)
                subprocess.Popen(['install_name_tool', '-change', libpath, "@executable_path/" + libpath, f])
    if missing:
        find_n_fix_missing(missing)

includes = []
excludes = ['Tkinter', 'readline']

freezer = Freezer('dist/freeze/Config_Editor', includes=includes, excludes=excludes)
freezer.addScript('src/configeditor.py', gui_only=True)
freezer.include_py = False
freezer.use_compression = True
freezer()

if sys.platform == 'darwin':
    os.chdir(freezer.distdir)
    find_n_fix_missing(glob.glob("*.so") + glob.glob("*.dylib"))