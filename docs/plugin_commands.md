# Adding commands from a plugin

A plugin can register custom commands by using the following code in the plugin:

```python
def register_commands():
    @command.command("What is your name?")
    def ask_the_name(name):
        print name


try:
    from qgiscommand import command
    register_commands()
except ImportError:
    pass
```

The `ImportError` check is there so no error is raised to the user when the `Command Bar` plugin is not installed.  If the `Command Bar` plugin is installed the `command` module will be imported and the `register_commands` function is called.  You can register your custom command by following the API guide.