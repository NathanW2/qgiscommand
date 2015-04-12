import inspect

commands = {}
func_args = {}
help_text = {}

# Validators is a dict of function names and with a dict of argname and check function
validators = {}

def escape_name(funcname):
    funcname = funcname.replace("_","-")
    funcname = funcname.replace(" ","-")
    return funcname.lower()

def command(*prompts):
    def wrapper(func):
        name = escape_name(func.__name__)
        func_args[name] = list(reversed(prompts))
        commands[name] = func
        help_text[name] = func.__doc__
        return func
    return wrapper


def check(**checks):
    def wrapper(func):
        name = escape_name(func.__name__)
        block = validators.setdefault(name, {})
        block.update(checks)
        validators[name] = block
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


def validators_for_function(funcname):
    return validators.get(funcname, {})


def line_valid(line, checks, args, argdata):
    for name, checkfunc in checks.iteritems():
        try:
            index = args.index(name)
            data = argdata[index]
            return checkfunc(data)
        except IndexError:
            continue
    return True, ""

def data_valid(data, argname, checks):
    try:
        func = checks[argname]
        return func(data)
    except KeyError:
        return True, ""
        
def parse_line(line):
    print "PARSE,", line
    data = line.split()
    line = line.strip()
    if not data or not line:
        return

    funcname = data[0]
    argdata = []
    try:
        funcdef = commands[funcname]
        if not inspect.isfunction(funcdef):
            func = funcdef[0]
            funcname = escape_name(func.__name__)
            args = funcdef[1]
            argdata += args
        else:
            func = funcdef
    except KeyError:
        print "No function called {}".format(funcname)
        return

    # Add the args that have been already set for this function
    args = data[1:]
    argdata += args
    return funcname, func, argdata

def parse_line_data(line):
    funcname, func, argdata = parse_line(line)

    needed, _, _, _ = inspect.getargspec(func)
    if not needed:
        func()
        return

    _validators = validators_for_function(funcname)

    # If the full input line is not valid we have to wait here until it is done
    valid, reason = line_valid(line, _validators, needed, argdata)
    while not valid:
        prompt = "(Error: {})".format(reason)
        data = "{} {}".format(funcname, " ".join(argdata))
        line = yield prompt, data
        funcname, func, argdata = parse_line(line)
        valid, reason = line_valid(line, _validators, needed, argdata)
        
    neededcount = len(needed)
    wehavecount = len(argdata)
    if neededcount > wehavecount:
        prompts = list(reversed(func_args[funcname]))
        prompts = prompts[wehavecount:]
        for argindex, prompt in enumerate(prompts):
            _line = "({}) {}".format(funcname, prompt)
            data = yield _line, None
            argname = needed[argindex]
            valid, reason = data_valid(data, argname, _validators)
            while not valid:
                _line = "({}) {} ({})".format(funcname, prompt, reason)
                data = yield _line, data
                valid, reason = data_valid(data, argname, _validators)
                    
            argdata.append(data)

    print func
    func(*argdata)

        
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
            prompt, data = gen.send(None)
            while True:
                inputdata = raw_input(prompt + " ")
                print inputdata
                prompt, data = gen.send(inputdata)
        except StopIteration:
            continue


if __name__ == "__main__":
    runloop()

# Qt Widget
