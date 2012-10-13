#!/usr/bin/env python

from PySide.QtGui import QApplication
from jsonConfig.editor import ConfigEditor
import os, defaults

if __name__ == '__main__':
    app = QApplication([])
    cfg = defaults.get_config()
    cfg.set_user_file(defaults.get_user_file())
    editor = ConfigEditor(app, cfg, 'Space Fortress Config Editor')
    plugins = {}
    plugins = defaults.load_plugins(editor, defaults.get_plugin_home(), plugins)
    for name in plugins:
        try:
            plugins[name].eventCallback(None, None, None, "config", "load", "defaults")
        except AttributeError:
            pass
    editor.setup()
    app.exec_()
