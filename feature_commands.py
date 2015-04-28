from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

import command


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


@command.command("Latitude in DMS?", "Longitude in DMS?")
def dms(lat, lon):
    """
    Add a point at the lat and lon for the current layer using DMS notation
    """

    lat, lon = lat, lon

    l_lat = lat.upper().split()
    l_lon = lon.upper().split()

    # need to add validation tests

    if l_lat[3] == 'N':
        ddlat = float(l_lat[0]) + (float(l_lat[1]) / 60) + float(l_lat[2]) / 3600
    elif l_lat[3] == 'S':
        ddlat = (float(l_lat[0]) + float(l_lat[1]) / 60 + float(l_lat[2]) /
                 3600) * -1
    else:
        ddlat = '0'

    if l_lon[3] == 'E':
        ddlon = float(l_lon[0]) + float(l_lon[1]) / 60 + float(l_lon[2]) / 3600
    elif l_lon[3] == 'W':
        ddlon = (float(l_lon[0]) + float(l_lon[1]) / 60 + float(l_lon[2]) /
                 3600) * -1
    else:
        ddlon = '0'

    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    geom = QgsGeometry.fromPoint(QgsPoint(ddlon, ddlat))
    f.setGeometry(geom)
    layer.addFeature(f)
    iface.mapCanvas().refresh()


@command.command("Latitude in DMS?", "Longitude in DMS?")
def feature_move_dms(lat, lon):
    """
    Add a point at the lat and lon for the current layer using DMS notation
    """

    lat, lon = lat, lon

    l_lat = lat.upper().split()
    l_lon = lon.upper().split()

    # need to add validation tests

    if l_lat[3] == 'N':
        ddlat = float(l_lat[0]) + (float(l_lat[1]) / 60) + float(l_lat[2]) / 3600
    elif l_lat[3] == 'S':
        ddlat = (float(l_lat[0]) + float(l_lat[1]) / 60 + float(l_lat[2]) /
                 3600) * -1
    else:
        ddlat = '0'

    if l_lon[3] == 'E':
        ddlon = float(l_lon[0]) + float(l_lon[1]) / 60 + float(l_lon[2]) / 3600
    elif l_lon[3] == 'W':
        ddlon = (float(l_lon[0]) + float(l_lon[1]) / 60 + float(l_lon[2]) /
                 3600) * -1
    else:
        ddlon = '0'

    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    selection = layer.selectedFeatures()
    selection_comparison = len(selection) == 1
    if selection_comparison == True:
        fgeom = selection[0].geometry()
        geom = QgsGeometry.fromPoint(QgsPoint(ddlon, ddlat))
        vector = fgeom.asPoint() == geom.asPoint()
        if vector:
            #return True, 'same coordinates nothing changed'
            pass
        else:
            layer.changeGeometry(selection[0].id(), geom)
            iface.mapCanvas().refresh()
    else:
        #return False,'none or more than 1 point selected'
        pass


@command.command("Latitude in DMS?", "Longitude in DMS?")
def feature_move(x, y):
    """
    Moves a point to the x and y for the current layer
    """
    x, y = float(x), float(y)
    layer = iface.activeLayer()
    f = QgsFeature(layer.pendingFields())
    selection = layer.selectedFeatures()
    selection_comparison = len(selection) == 1
    if selection_comparison == True:
        fgeom = selection[0].geometry()
        geom = QgsGeometry.fromPoint(QgsPoint(x, y))
        vector = fgeom.asPoint() == geom.asPoint()
        if vector:
            #return True, 'same coordinates nothing changed'
            pass
        else:
            layer.changeGeometry(selection[0].id(), geom)
            iface.mapCanvas().refresh()
    else:
        #return False,'none or more than 1 point selected'
        pass
