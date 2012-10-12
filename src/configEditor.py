#!/usr/bin/env python

import sys, os
from PySide.QtGui import *

import defaults
from jsonConfig import ConfigEditor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cfg = defaults.get_config()
    cfg.set_user_file(defaults.get_user_file())
    editor = ConfigEditor(app, cfg, 'Spacefortress Config Editor')
    i = sys.argv[0].rfind('/')
    if i != -1:
        approot = sys.argv[0][:sys.argv[0].rfind('/')]
    else:
        approot = './'
    plugins = {}
    sys.path.append(os.path.join(approot, 'Plugins', 'pycogworks'))
    plugins = defaults.load_plugins(editor, os.path.join(approot, 'Plugins'), plugins)
    plugins = defaults.load_plugins(editor, defaults.get_plugin_home(), plugins)
    for name in plugins:
        try:
            plugins[name].eventCallback(None, None, None, "config", "load", "defaults")
        except AttributeError:
            pass
    editor.setup()
    sys.exit(app.exec_())
