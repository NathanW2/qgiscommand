from qgis.core import QgsMessageLog

try:
    import local_settings
    log_it = local_settings.log_it
    category = local_settings.category
except ImportError:
    log_it = False


def msg(txt):
    if log_it:
        QgsMessageLog.logMessage("{} id:{}".format(txt, id(msg)), category)
