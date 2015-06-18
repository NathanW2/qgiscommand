# API

Functions that can be used as commands should defined with the `@command.command` function.
This function takes a list of questions for each argument. At the moment you must set all questions for all
args in the function.

Here is an example function that will open the attribute table for the given layer name

```python
@command.command("Layer name (Empty for active layer)?")
def table(tablename):
    if not tablename.strip():
        layer = iface.activeLayer()
    else:
        layer = layer_by_name(tablename)
    iface.showAttributeTable(layer)
```

Functions with `_` in the name will be auto converted to `-` for use in the command bar.  Functions are also forced to be lowercase.

```python
@command.command()
def my_function():
    pass
```

Can be called as `my-function`

If you need to define more then one prompt you can do it like this `@command.coomand("Message 1", "Message 2")` with each one matching
the argument you function takes

### Auto Complete

Auto complete functions should return a list of values to be used by the auto complete list in the bar

```python
def vector_layers(argname, data):
    return [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
```

```python
def names(argname, data):
    return ["Bob", "Jane", "Foo"]
```
 
The `argname` and `data` hold the current name of the argument being used for completion and the data
the user is typing. You can ignore it or use it to pre filter the list

**Note:** The command bar already does fuzzy matching so you may or may not need to pre filter.

Use `@command.complete_with` to set the completer for a arg

```python
@command.command("layer name")
@command.complete_with(tablename=vector_layers)
def table(tablename):
    pass
```

You can also use the `@command.complete_name("Name")` function to give the auto complete list
a nice name

```python
@command.complete_name("Pick a user name?")
def names(argname, data):
    return ["Bob", "Jane", "Foo"]
```

### Validation

Validation functions should take a single argument which is the current data for that arg

```python
def is_vector_layer(data):
    """
    Check if a given layer name is a vector layer or not
    """
    try:
        layer = layer_by_name(data)
        vector = layer.type() == QgsMapLayer.VectorLayer
        if vector:
            return True, ""
        else:
            return False, "Is not vector layer"
    except IndexError:
        return False, "Layer not found"
```

You should return a tuple of `False, "Reason"`, or `True, ""` to tell the command bar if the check passes or fails

You can set a validation function on your command function using the `@command.check` function. `check` takes a keywords args of argument names and function

```python
@command.command("layer name")
@command.check(tablename=is_vector_layer)
def table(tablename):
    pass
```
