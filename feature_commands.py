from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

import command


def dms_to_dd(lat, lon):
    l_lat = lat.upper().split()
    l_lon = lon.upper().split()

    ddlat = float(l_lat[0]) + (float(l_lat[1]) / 60) + float(l_lat[2]) / 3600
    if l_lat[3] == 'S':
        ddlat *= -1

    ddlon = float(l_lon[0]) + float(l_lon[1]) / 60 + float(l_lon[2]) / 3600
    if l_lon[3] == 'W':
        ddlon *= -1
    else:
        ddlon = '0'

    return ddlat, ddlon


@command.command("x", "y")
def point_at(x, y):
    """
    Add a point at the x and y for the current layer
    """
    x, y = float(x), float(y)
    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    geom = QgsGeometry.fromPoint(QgsPoint(x, y))
    f.setGeometry(geom)
    layer.addFeature(f)
    iface.mapCanvas().refresh()


@command.command("Latitude in DMS?", "Longitude in DMS?", alias=['dms'])
def point_at_dms(lat, lon):
    """
    Add a point at the lat and lon for the current layer using DMS notation
    """

    ddlat, ddlon = dms_to_dd(lat, lon)

    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    geom = QgsGeometry.fromPoint(QgsPoint(ddlon, ddlat))
    f.setGeometry(geom)
    layer.addFeature(f)
    iface.mapCanvas().refresh()


@command.command("Latitude in DMS?", "Longitude in DMS?", alias=['move-dms'])
def feature_move_dms(lat, lon):
    """
    Add a point at the lat and lon for the current layer using DMS notation
    """

    ddlat, ddlon = dms_to_dd(lat, lon)

    layer = iface.activeLayer()
    selection = layer.selectedFeatures()
    update = False
    for feature in selection:
        fgeom = feature.geometry()
        geom = QgsGeometry.fromPoint(QgsPoint(ddlon, ddlat))
        same = fgeom.asPoint() == geom.asPoint()
        if not same:
            layer.changeGeometry(feature.id(), geom)
            update = True
    if update:
        iface.mapCanvas().refresh()


@command.command("x", "y")
def feature_move(x, y):
    """
    Moves a point to the x and y for the current layer
    """
    x, y = float(x), float(y)

    layer = iface.activeLayer()
    selection = layer.selectedFeatures()
    update = False
    for feature in selection:
        fgeom = feature.geometry()
        geom = QgsGeometry.fromPoint(QgsPoint(x, y))
        same = fgeom.asPoint() == geom.asPoint()
        if not same:
            layer.changeGeometry(feature.id(), geom)
            update = True
    if update:
        iface.mapCanvas().refresh()
