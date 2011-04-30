import sys
from cx_Freeze import setup, Executable

includes = []
excludes = ['pkg_resources','email','distutils','PySide','Tkinter','nose','ssl','xml','numpy','multiprocessing']
packages = []
path = []
icon = None
include_files = ['fonts/freesansbold.ttf',
				'gfx/exp.png',
				'sounds/Collision.wav',
				'sounds/ExpShip.wav',
				'sounds/ShellFired.wav',
				'sounds/bonus_fail.wav',
				'sounds/ExpFort.wav',
				'sounds/MissileFired.wav',
				'sounds/VulnerZeroed.wav',
				'sounds/bonus_success.wav']
zip_includes = []

base = None
if sys.platform == 'win32':
	base = 'Win32GUI'
elif sys.platform == 'darwin':
	packages = ['pygame.macosx']
	
spacefortress = Executable(
	script = 'PSF5.py',
	compress = True,
	base = base,
	copyDependentFiles = True,
	appendScriptToExe = False,
	appendScriptToLibrary = False,
	icon = icon,
)

setup(
	version = '5.0',
	description = '2D frictionless space shooter for psycological research',
	author = 'Marc Destefano and Ryan Hope',
	name = 'SpaceFortress',
	options = {'build_exe': {
							'includes': includes,
							'excludes': excludes,
				 			'packages': packages,
			 				'path': path,
                 			'include_files': include_files,
                 			'zip_includes': zip_includes
				 }},
	executables = [spacefortress]
)