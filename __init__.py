#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import qgiscommand


def classFactory(iface):
    return CommandBar(iface)


class CommandBar:
    def __init__(self, iface):
        self.iface = iface
        self.shell = qgiscommand.CommandShell(iface.mapCanvas())
        self.short = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Semicolon), iface.mainWindow())
        self.short.setContext(Qt.ApplicationShortcut)
        self.short.activated.connect(self.shell.activated)
        self.shortDE = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Comma), iface.mainWindow())
        self.shortDE.setContext(Qt.ApplicationShortcut)
        self.shortDE.activated.connect(self.shell.activated)

    def initGui(self):
        self.action = QAction("Open Command Bar!", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        self.shell.activated()
