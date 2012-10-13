from bbfreeze import Freezer
import shutil, glob, os

includes = []
excludes = ['Tkinter', 'readline']

freezer = Freezer('dist/freeze/Config_Editor', includes=includes, excludes=excludes)
freezer.addScript('src/configeditor.py', gui_only=True)
freezer.include_py = False
freezer.use_compression = True
freezer()

for f in glob.glob("/usr/lib/libpyside-*"):
    shutil.copy(f, os.path.join(freezer.distdir, os.path.split(f)[1]))
for f in glob.glob("/usr/lib/libshiboken-*"):
    shutil.copy(f, os.path.join(freezer.distdir, os.path.split(f)[1]))