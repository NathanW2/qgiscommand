Defining user commands
-------------------------------------------------------------------------------

New commands can be defined in Python files which are loaded from `.qgis2\python\commandbar`. The `commandbar` folder is created when the plugin first loads.

Lets say you want to define a function that shows a message in the message bar.  Create a `myfunctions.py` in the commandbar folder with the following code

```python
from qgis.utils import iface
from qgiscommand.command import command

@command()
def my_function():
    iface.messageBar().pushInfo("test", "test")
```

When the plugin loads `my-function` will be avaiable to use.

**Tip**: You can also reload all the user packages using the `reload-packages` command

