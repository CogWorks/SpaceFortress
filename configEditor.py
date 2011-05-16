#!/usr/bin/env python

import sys
from PySide.QtGui import *

import defaults
from config.editor import ConfigEditor
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    cfg = defaults.get_config()
    cfg.set_user_file(defaults.get_user_file())
    editor = ConfigEditor(app, cfg, 'Spacefortress Config Editor')
    plugins = defaults.load_plugins(editor, defaults.get_plugin_home())
    for name in plugins:
        try:
            plugins[name].eventCallback(None, None, None, "config", "load", "defaults")
        except AttributeError:
            pass
    editor.setup()
    sys.exit(app.exec_())