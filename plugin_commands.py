"""
Module to handle commands to do with plugin management.
"""

import command
import plugin_commands

from pyplugin_installer import installer as plugin_installer

plugins_fetched = False


def fetch_plugins():
    installer = plugin_installer.pluginInstaller
    if not plugins_fetched:
        installer.fetchAvailablePlugins(True)
        global plugins_fetched
        plugins_fetched = True


def plugin_name_map():
    return {
        plugin['name']: plugin['id']
        for plugin in plugin_installer.plugins.all().values()
    }


def plugins_for_install(argdata, userdata):
    fetch_plugins()
    return plugin_name_map().keys()


def installed_plugins(argdata, userdata):
    fetch_plugins()
    status = ['installed', 'upgradeable']
    return [plugin['name']
            for plugin in plugin_installer.plugins.all().values()
            if plugin['status'] in status]


def is_plugin(name):
    # Fetch plugins only runs once per session
    fetch_plugins()
    installer = plugin_installer.pluginInstaller
    try:
        pluginid = plugin_name_map()[name]
        plugin_installer.plugins.all()[pluginid]
        return True, ""
    except KeyError:
        return False, "Plugin not found in installer"


@command.command("Plugin name")
@command.check(name=is_plugin)
@command.complete_with(name=plugins_for_install)
def plugin_install(name):
    print name
    installer = plugin_installer.pluginInstaller
    pluginid = plugin_name_map()[name]
    installer.installPlugin(pluginid)


@command.command("Plugin name")
@command.check(name=is_plugin)
@command.complete_with(name=installed_plugins)
def plugin_uninstall(name):
    print name
    installer = plugin_installer.pluginInstaller
    pluginid = plugin_name_map()[name]
    installer.uninstallPlugin(pluginid, quiet=True)
