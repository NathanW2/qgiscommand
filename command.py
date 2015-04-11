import inspect

commands = {}
func_args = {}
help_text = {}

def escape_name(funcname):
    funcname = funcname.replace("_","-")
    funcname = funcname.replace(" ","-")
    return funcname

def command(*prompts):
    def wrapper(func):
        name = escape_name(func.__name__)
        func_args[name] = list(reversed(prompts))
        commands[name] = func
        help_text[name] = func.__doc__
        return func
    return wrapper

@command("Alias", "Function Name", "Args")
def alias(alias, name, *args):
    """
    Register a alias for a function and pre set arguments
    """
    args = " ".join(args)
    args = args.split()
    func = commands[escape_name(name)]
    commands[alias] = (func, args)


def parse_line_data(line):
    data = line.split()
    if not data or not line.strip():
        return

    funcname = data[0]
    argdatas = []
    try:
        funcdef = commands[funcname]
        if not inspect.isfunction(funcdef):
            func = funcdef[0]
            funcname = escape_name(func.__name__)
            args = funcdef[1]
            argdatas += args
        else:
            func = funcdef
    except KeyError:
        print "No function called {}".format(funcname)
        return

    # Add the args that have been already set for this function
    args = data[1:]
    argdatas += args

    needed, _, _, _ = inspect.getargspec(func)
    if not needed:
        func()
        return
        
    neededcount = len(needed)
    wehavecount = len(argdatas)
    if neededcount > wehavecount:
        prompts = list(reversed(func_args[funcname]))
        prompts = prompts[wehavecount:]
        for prompt in prompts:
            argdata = yield "({}) {}:".format(funcname, prompt)
            argdatas.append(argdata)

    func(*argdatas)

## Command line version.

def runloop():
    import readline

    while True:
        line = raw_input('-> ')
        if line == 'stop':
            break

        gen = parse_line_data(line)
        if not gen:
            continue

        try:
            prompt = gen.send(None)
            while True:
                prompt = gen.send(raw_input(prompt + " "))
        except StopIteration:
            continue


if __name__ == "__main__":
    runloop()

# Qt Widget

