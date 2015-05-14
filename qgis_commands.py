import os
import glob

from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

from PyQt4.QtGui import QDockWidget

import command

from plugin_commands import *
from feature_commands import *

import logger

# logger.msg('Test message from qgis_commands.py')


def layer_by_name(layername):
    return QgsMapLayerRegistry.instance().mapLayersByName(layername)[0]


project_paths = []

@command.command("Paths?")
def define_project_paths(paths):
    global project_paths
    project_paths = paths.split(',')


def complete_projects(argname, data):
    # TODO Add auto complete for paths
    projects = []
    for path in project_paths:
        projects += [os.path.basename(f) for f in glob.glob(path + "/*.qgs")]
    return projects

@command.command("Name")
def new_group(name):
    tree = iface.layerTreeView()
    current = tree.currentGroupNode()
    current.addGroup(name)


@command.command("Name")
@command.complete_with(name=complete_projects)
def load_project(name):
    """
    Load a project from the set project paths
    """
    _name = name
    ## name += ".qgs"
    for path in project_paths:
        for root, dirs, files in os.walk(path):
            if name in files:
                path = os.path.join(root, name)
                iface.addProject(path)
                return
    iface.addProject(_name)


@command.command()
def hide_docks():
    docks = iface.mainWindow().findChildren(QDockWidget)
    for dock in docks:
        dock.setVisible(False)


def layers(argname, data):
    """
    Return all the layers loaded in this session
    """
    return [layer.name()
            for layer in QgsMapLayerRegistry.instance().mapLayers().values()]


def vector_layers(argname, data):
    """
    Return all the vector layers loaded in this session
    """
    return [layer.name()
            for layer in QgsMapLayerRegistry.instance().mapLayers().values()]


def is_vector_layer(data):
    try:
        layer = layer_by_name(data)
        vector = layer.type() == QgsMapLayer.VectorLayer
        if vector:
            return True, ""
        else:
            return False, "Is not vector layer"
    except IndexError:
        return False, "Layer not found"


@command.command("layer name")
@command.complete_with(tablename=vector_layers)
@command.check(tablename=is_vector_layer)
def table(tablename):
    if not tablename.strip():
        layer = iface.activeLayer()
    else:
        layer = layer_by_name(tablename)
    iface.showAttributeTable(layer)
