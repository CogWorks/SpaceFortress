import sys
from cx_Freeze import setup, Executable

includes = []
excludes = []
packages = []
path = []
icon = None
include_files = []
zip_includes = []

base = None
if sys.platform == 'win32':
	base = 'Win32GUI'

configedit = Executable(
	script='configEditor.py',
	compress=True,
	base=base,
	copyDependentFiles=True,
	appendScriptToExe=False,
	appendScriptToLibrary=False,
	icon=icon,
)

setup(
	version='1.0',
	description='Config editor for Space Fortress 5',
	author='Marc Destefano and Ryan Hope',
	name='configEditor',
	options={'build_exe': {
							'includes': includes,
							'excludes': excludes,
				 			'packages': packages,
			 				'path': path,
                 			'include_files': include_files,
                 			'zip_includes': zip_includes
				 }},
	executables=[configedit]
)
