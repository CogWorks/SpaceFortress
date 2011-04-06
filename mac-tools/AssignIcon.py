#!/usr/bin/env python

import string, sys, os, shutil, tempfile

file = "/usr/bin/file"
osascript = "/usr/bin/osascript"
sips = "/usr/bin/sips"

setfile = "/Developer/Tools/SetFile"
rez = "/Developer/Tools/Rez"
derez = "/Developer/Tools/DeRez"

usedcliapps = [file, osascript, sips, setfile, rez, derez]	

def getMyBaseName():
	return os.path.basename(sys.argv[0])

def displayUsage():
	print "Usage: "+getMyBaseName()+" [image] [target]"
	print " "
	print " [image]    is the image file to be used as the icon"
	print " [target]   is the target file or folder to assign"
	print "            the icon to"
	print " "

def isImage(f):
	o = os.popen(file+" -p \""+f+"\"", "r")
	if (o.read().find("image") != -1):
		return True
	else:
		return False

def runInShell(cmd):
	os.popen(cmd, 'r')

for i in usedcliapps:
	if not os.path.exists(i):
		print "Error! "+i+" does not exist!"
		print " "
		sys.exit(127)

if len(sys.argv)<3:
	displayUsage()
	sys.exit(0)

source = sys.argv[1]
target = sys.argv[2]

if os.path.exists(source):
	if os.path.exists(target):
		if isImage(source):
			
			tempfile.gettempdir()
			shutil.copyfile(source, tempfile.tempdir+"/temp-pic")
			runInShell(sips+" -i \""+tempfile.tempdir+"/temp-pic\"")
			runInShell(derez+" -only icns \""+tempfile.tempdir+"/temp-pic\" > \""+tempfile.tempdir+"/temprsrc.rsrc\"")
			if os.path.isdir(target):
				runInShell(rez+" -append \""+tempfile.tempdir+"/temprsrc.rsrc\" -o \"`printf \""+target+"/Icon\\r\"`\"")
			else:
				runInShell(rez+" -append \""+tempfile.tempdir+"/temprsrc.rsrc\" -o \""+target+"\"")
			runInShell(setfile+" -a C \""+target+"\"")
			runInShell(setfile+" -a V \"`printf \""+target+"/Icon\\r\"`\"")
			os.remove(tempfile.tempdir+"/temp-pic")
			os.remove(tempfile.tempdir+"/temprsrc.rsrc")
			
		else:
			print "Error! "+source+" is not an image file"
			print " "
			sys.exit(127)
	else:
		print "Error! "+target+" does not exist"
		print " "
		sys.exit(127)
else:
	print "Error! "+source+" does not exist"
	print " "
	sys.exit(127)





