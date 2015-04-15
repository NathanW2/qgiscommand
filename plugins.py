import command

from pyplugin_installer import installer as plugin_installer

plugins_fetched = False

def fetch_plugins():
    installer = plugin_installer.pluginInstaller
    if not plugins_fetched:
        installer.fetchAvailablePlugins(True)
        global plugins_fetched
        plugins_fetched = True


def plugins_for_install(argdata, userdata):
    fetch_plugins()
    return [plugin['name'] for plugin in plugin_installer.plugins.all().values()] 


def installed_plugins(argdata, userdata):
    fetch_plugins()
    status = ['installed', 'upgradeable']
    return [plugin['name'] for plugin in plugin_installer.plugins.all().values() if plugin['status'] in status] 


def is_plugin(name):
    # Fetch plugins only runs once per session
    fetch_plugins()
    installer = plugin_installer.pluginInstaller
    try:
        plugin_installer.plugins.all()[name]
        return True, ""
    except KeyError:
        return False, "Plugin not found in installer"


@command.command("Plugin name")
@command.check(name=is_plugin)
@command.complete_with(name=plugins_for_install)
def plugin_install(name):
    installer = plugin_installer.pluginInstaller
    installer.installPlugin(name)


@command.command("Plugin name")
@command.check(name=is_plugin)
@command.complete_with(name=installed_plugins)
def plugin_uninstall(name):
    installer = plugin_installer.pluginInstaller
    installer.uninstallPlugin(name, quiet=True)
