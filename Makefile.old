.PHONY: macosx

all: macosx

macosx: macosx/Space\ Fortress.app macosx/Config\ Editor.app
	@osx=10.`sw_vers -productVersion | cut -f 2 -d "."`;\
	ver=`./version.py`;\
	cd macosx; \
	productbuild \
		--component Space\ Fortress.app /Applications/Space\ Fortress\ 5 \
		--component Config\ Editor.app /Applications/Space\ Fortress\ 5 \
		SpaceFortress-$$ver-x86_64-macosx$$osx.pkg 

macosx/Space\ Fortress.app: sf-dist/dist
	@mkdir -p macosx/Space\ Fortress.app/Contents/MacOS
	@mkdir -p macosx/Space\ Fortress.app/Contents/Resources
	@cp -r sf-dist/dist/* macosx/Space\ Fortress.app/Contents/MacOS/
	@cp -r fonts macosx/Space\ Fortress.app/Contents/MacOS/
	@cp -r gfx macosx/Space\ Fortress.app/Contents/MacOS/
	@cp -r sounds macosx/Space\ Fortress.app/Contents/MacOS/
	@cp psf5.png macosx/Space\ Fortress.app/Contents/MacOS/
	@cp psf5.icns macosx/Space\ Fortress.app/Contents/Resources/
	@osx=10.`sw_vers -productVersion | cut -f 2 -d "."`;\
	ver=`./version.py`;\
	cat Info.plist.sf | sed s/SFVERSION/"$$ver"/ | sed s/OSXVERSION/"$$osx"/ > macosx/Space\ Fortress.app/Contents/Info.plist
	@echo "APPL????" > macosx/Space\ Fortress.app/Contents/PkgInfo
	@SetFile -a B macosx/Space\ Fortress.app
	
macosx/Config\ Editor.app: ce-dist/dist
	@mkdir -p macosx/Config\ Editor.app/Contents/MacOS
	@mkdir -p macosx/Config\ Editor.app/Contents/Resources
	@cp -r ce-dist/dist/* macosx/Config\ Editor.app/Contents/MacOS/
	@cp prefs.icns macosx/Config\ Editor.app/Contents/Resources/
	@osx=10.`sw_vers -productVersion | cut -f 2 -d "."`;\
	ver=`./version.py`;\
	cat Info.plist.ce | sed s/SFVERSION/"$$ver"/ | sed s/OSXVERSION/"$$osx"/ > macosx/Config\ Editor.app/Contents/Info.plist
	@echo "APPL????" > macosx/Config\ Editor.app/Contents/PkgInfo
	@SetFile -a B macosx/Config\ Editor.app

sf-dist/dist:
	@mkdir -p sf-dist
	@cd sf-dist; bb-freeze ../PSF5.py

ce-dist/dist:
	@mkdir -p ce-dist
	@cd ce-dist; bb-freeze ../configEditor.py
		
clean:
	@rm -rf sf-dist
	@rm -rf `find . -name "*.pyc"`
	@rm -rf `find . -name "*.pyo"`