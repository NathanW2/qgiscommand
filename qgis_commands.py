import os

from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

import command

project_paths = []

@command.command("What is the x?", "What is the y?")
def point_at(x, y):
    """
    Add a point at the x and y for the current layer
    """
    x,y = float(x), float(y)
    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    geom = QgsGeometry.fromPoint(QgsPoint(x,y))
    f.setGeometry(geom)
    layer.addFeature(f)
    iface.mapCanvas().refresh()

@command.command("Paths?")
def define_project_paths(paths):
    global project_paths
    project_paths = paths.split(',')

@command.command("Name")
def load_project(name):
    """
    Load a project from the set project paths
    """
    _name = name
    name += ".qgs"
    for path in project_paths:
        for root, dirs, files in os.walk(path):
            if name in files:
                path = os.path.join(root, name)
                iface.addProject(path)
                return
    iface.addProject(_name)

@command.command("Latitude in DMS?", "Longitude in DMS?")
def DMS (lat, lon):
    """
    Add a point at the lat and lon for the current layer using DMS notation
    """

    lat,lon = float(lat), float(lon)
    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    geom = QgsGeometry.fromPoint(QgsPoint(lon,lat))
    f.setGeometry(geom)
    layer.addFeature(f)
    iface.mapCanvas().refresh()