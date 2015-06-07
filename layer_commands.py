import re
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
from qgis.utils import iface
from command import command, complete_with, check
from qgis_commands import layer_by_name, layers


def layer_exists(data):
    try:
        layer_by_name(data)
        return True, ""
    except IndexError:
        return False, "Layer not found"

layernamecache = None


def update_names(argname, userdata):
    if not userdata:
        userdata = ''

    if not layernamecache:
        global layernamecache
        _layers = QgsMapLayerRegistry.instance().mapLayers().values()
        layernamecache = {layer.name(): layer for layer in _layers}

    data = userdata.split('/')
    if not len(data) == 2:
        for name, layer in layernamecache.iteritems():
            layer.setLayerName(name)
        return []

    try:
        for name, layer in layernamecache.iteritems():
            newname = re.sub(data[0], data[1], name)
            layer.setLayerName(newname)
    except re.error:
        return []
    return []


def undo_names():
    """
    Undo any name changes that have happened during the command
    """
    for name, layer in layernamecache.iteritems():
        layer.setLayerName(name)


@command("Layer name")
@complete_with(layer=layers)
@check(layer=layer_exists)
def set_active_layer(layer):
    """
    Set the active layer in the current session
    """
    layer = layer_by_name(layer)
    iface.setActiveLayer(layer)

@command("Regex")
@complete_with(regex=update_names)
def rename_layers(regex):
    """
    Rename the layer names using regex.

    Regex format:  {regex}/{replace with}
    Example: rename_layers "water|sewer/pipe layers --"
    """
    global layernamecache
    layernamecache = None
    return