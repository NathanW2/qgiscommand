Defining user commands
-------------------------------------------------------------------------------

The best way to get started adding you own user commands is to run `define-package {name}`. A new file will be created in `.qgis2\python\commandbar`
and opened in your editor that you have set.  This is just normal Python so hack away adding your own commands. Save the file and run
`reload-packages` your new functions will show up in the list in the command auto complete. Hell yeah! Hack all the things!

Here is a basic example. Lets say you want to define a function that shows a message in the message bar.

First lets define a new package call `mymessagefunctions`. Run `define-package mymessagefunctions`

```python
from qgis.utils import iface
from qgiscommand.command import command

@command("What message do you want to show?")
def show_my_message(message):
    iface.messageBar().pushInfo("My message bar", message)
```

Save the file and back in the command bar we run `reload-packages`.  We can now call
`show-my-message`. Sweet!

**Note**: `reload-packages` reloads all user packages.

Easy as that.

Follow the API guide for more options that can be used with your comamnds. 
