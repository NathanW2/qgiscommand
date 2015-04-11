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

    lat,lon = lat, lon

    l_lat = lat.upper().split()
    l_lon = lon.upper().split()

    # need to add validation tests

    if l_lat[3] == 'N':
        ddlat = float(l_lat[0])+float(l_lat[0])/60+float(l_lat[0])/3600
    elif l_lat[3] == 'S':
        ddlat = (float(l_lat[0])+float(l_lat[0])/60+float(l_lat[0])/3600)*-1
    else:
        ddlat = '0'

    if l_lon [3] == 'E':
        ddlon = float(l_lon[0])+float(l_lon[0])/60+float(l_lon[0])/3600
    elif l_lon[3] == 'W':
        ddlon = (float(l_lon[0])+float(l_lon[0])/60+float(l_lon[0])/3600)*-1
    else:
        ddlon = '0'

    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    geom = QgsGeometry.fromPoint(QgsPoint(ddlon,ddlat))
    f.setGeometry(geom)
    layer.addFeature(f)
    iface.mapCanvas().refresh()