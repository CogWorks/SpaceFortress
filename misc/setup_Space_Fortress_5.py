from bbfreeze import Freezer
import zipfile, os

includes = []
excludes = ['Tkinter', 'readline']
 
freezer = Freezer('dist/freeze/Space_Fortress_5', includes=includes, excludes=excludes)
freezer.addScript('src/spacefortress5.py', gui_only=True)
freezer.include_py = False
freezer.use_compression = True
freezer()

z = zipfile.ZipFile(os.path.join(freezer.distdir, 'library.zip'), 'a')
os.chdir('src')
for base, dirs, files in os.walk('resources'):
    for file in files:
        z.write(os.path.join(base,file))
z.close()