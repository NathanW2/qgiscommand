# API

### Auto Complete

Auto complete functions should return a list of values to be used by the auto complete list in the bar

```python
def vector_layers(argname, data):
    return [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
```

Use `@command.complete_with` to set the completer for a arg

```python
@command.command("layer name")
@command.complete_with(tablename=vector_layers)
def table(tablename):
    pass
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
