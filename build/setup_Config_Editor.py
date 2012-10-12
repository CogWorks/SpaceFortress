from bbfreeze import Freezer

includes = []
excludes = ['Tkinter', 'readline']

freezer = Freezer('dist/freeze/Config_Editor', includes=includes, excludes=excludes)
freezer.addScript('src/configeditor.py', gui_only=True)
freezer.include_py = False
freezer.use_compression = True
freezer()