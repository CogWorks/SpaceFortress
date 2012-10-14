PROJECTS	:= Space_Fortress_5 Config_Editor
BUNDLES		:= $(addsuffix .app,$(addprefix dist/bundles/,$(PROJECTS)))

APP_VERSION	:= $(shell python src/version.py)
OSX_VERSION	:= 10.$(shell sw_vers -productVersion | cut -f 2 -d ".")
ARCH		:= $(shell uname -m)

.SECONDARY: $(addprefix dist/freeze/,$(PROJECTS))

info:
	@echo "Usage: make [pkg|tag|clean]"

pkg: $(BUNDLES)
	productbuild $(subst .app,.app /Applications/Space\ Fortress\ 5,$(addprefix --component ,$?)) \
		dist/SpaceFortress-$(APP_VERSION)-$(ARCH)-macosx$(OSX_VERSION).pkg
	
dist/freeze/%:
	python misc/setup_$*.py
	
dist/bundles/%.app: dist/freeze/%
	mkdir -p $@/Contents/Resources
	cp icons/$*.icns $@/Contents/Resources/
	cp -r $? $@/Contents/MacOS
	echo "APPL????" > $@/Contents/PkgInfo
	cat misc/Info.plist.$* | sed s/SFVERSION/"$(APP_VERSION)"/ | sed s/OSXVERSION/"$(OSX_VERSION)"/ > $@/Contents/Info.plist
	SetFile -a B $@
	
clean:
	rm -rf dist
	rm -rf `find . -name "*.pyo"`
	rm -rf `find . -name "*.pyc"`
	
tag:
	git tag v$(APP_VERSION) -m "v$(APP_VERSION)"
	git push origin v$(APP_VERSION)
	
profile:
	python -m cProfile -o spacefortress5.prof src/spacefortress5.py 