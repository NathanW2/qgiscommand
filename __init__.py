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

import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from qgis.core import QgsApplication

import qgiscommand
import command


def classFactory(iface):
    return CommandBar(iface)


class CommandBar:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.iface.initializationCompleted.connect(self.qgis_loaded)
        self.shell = qgiscommand.CommandShell(self.iface.mapCanvas())
        self.shell.hide()

        self.short = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Semicolon), self.iface.mainWindow())
        self.short.setContext(Qt.ApplicationShortcut)
        self.short.activated.connect(self.shell.activated)
        self.shortDE = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Comma), self.iface.mainWindow())
        self.shortDE.setContext(Qt.ApplicationShortcut)
        self.shortDE.activated.connect(self.shell.activated)

        self.action = QAction("Open Command Bar!", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def qgis_loaded(self):
        # Read the init file from the python\commandbar folder
        folder = os.path.join(QgsApplication.qgisSettingsDirPath(), "python", "commandbar")
        initfile = os.path.join(folder, "init")
        try:
            os.makedirs(folder)
        except WindowsError:
            pass

        if not os.path.exists(initfile):
            header = "# Command bar init file. Lines starting with # are ignored"
            with open(initfile, "w") as f:
                f.write(header)
        command.load_from_file(initfile)

    def unload(self):
        self.iface.initializationCompleted.disconnect(self.qgis_loaded)
        self.shell.end()
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        self.shell.activated()
