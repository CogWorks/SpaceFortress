#!/usr/bin/env python

import sys, defaults

from PySide.QtGui import *
from config.editor import ConfigEditor
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    cfg = defaults.get_config()
    editor = ConfigEditor(cfg, 'Spacefortress Config Editor')
    sys.exit(app.exec_())
    
