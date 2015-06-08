import glob
import os
from qgis.core import QgsApplication
from command import command, complete_with

from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QDesktopServices

folder = os.path.join(QgsApplication.qgisSettingsDirPath(), "python",
                      "commandbar")


def packages(argname, data):
    return [os.path.basename(f) for f in glob.glob(folder + "/*.py")]


@command("Package name")
@complete_with(packagename=packages)
def edit_package(packagename):
    """
    Edit a package file
    """
    packagepath = os.path.join(folder, packagename)
    if not packagename.endswith(".py"):
        packagepath += ".py"

    open_file(packagepath)


def open_file(path):
    import subprocess
    try:
        subprocess.Popen([os.environ['EDITOR'], path])
    except KeyError:
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))


@command("Package name")
def define_package(packagename):
    """
    Define new command bar package file
    """
    packagename = packagename.replace(" ", "_")
    packagepath = os.path.join(folder, packagename) + ".py"
    with open(packagepath, 'w') as f:
        f.write("""# Package file for QGIS command bar plugin
                
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsApplication
from qgis.utils import iface
from qgiscommand.command import command, complete_with, check
from qgiscommand.qgis_commands import layer_by_name, layers


@command("Prompt")
def {0}_package_function(arg1):
    pass
                """.format(packagename))

    open_file(packagepath)
