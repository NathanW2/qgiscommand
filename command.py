import inspect

commands = {}
func_args = {}
help_text = {}

# Validators is a dict of function names and with a dict of argname and check function
validators = {}
completers = {}
sourcelookup = {}


class NoFunction(Exception):
    def __init__(self, message, funcname):
        super(NoFunction, self).__init__(message)
        self.funcname = funcname


def escape_name(funcname):
    funcname = funcname.replace("_", "-")
    funcname = funcname.replace(" ", "-")
    return funcname


def command(*prompts):
    (_, filename, line_number, _, _, _) = inspect.getouterframes(inspect.currentframe())[1]
    def wrapper(func):
        name = escape_name(func.__name__)
        func_args[name] = list(reversed(prompts))
        commands[name] = func
        help_text[name] = inspect.getdoc(func)
        sourcelookup[name] = (filename, line_number)
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


def complete_with(**functions):
    def wrapper(func):
        name = escape_name(func.__name__)
        block = completers.setdefault(name, {})
        block.update(functions)
        completers[name] = block
        return func
    return wrapper


def is_comamnd(commandname):
    if not commandname.strip():
        return False, "Function name can not be empty"
    if commandname in commands:
        return True,''
    else:
        return False, "No command found called {}".format(commandname)


def not_empty(value):
    if not value.strip():
        return False, "Value can no be empty"
    return True, ""


@command("Alias", "Function Name", "Args")
@check(name=is_comamnd, alias=not_empty)
def alias(alias, name, *args):
    """
    Register a alias for a function and pre set arguments
    """
    args = " ".join(args)
    args = args.split()
    func = commands[escape_name(name)]
    commands[alias] = (func, args)


def completions_for_arg(funcname, argname, userdata):
    try:
        completefunc = completers.get(funcname, {})[argname]
        return completefunc(argname, userdata)
    except KeyError:
        return []


def completions_for_line(line):
    if line.strip() == "":
        return commands.keys(), ""

    try:
        funcname, func, data = parse_line(line)
    except NoFunction as er:
        return commands.keys(), er.funcname

    args, _, _, _ = inspect.getargspec(func)
    index = len(data) - 1

    endofline = line.endswith(" ")
    if endofline:
        index += 1

    try:
        argname = args[index]
    except IndexError:
        return [], ""

    try:
        userdata = data[index]
    except IndexError:
        userdata = ''

    return completions_for_arg(funcname, argname, userdata), userdata


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
    """
    Parse the line and return the name of the called function, the Python function, and the data
    """
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
        raise NoFunction("No function called {}".format(funcname), funcname)

    # Add the args that have been already set for this function
    args = data[1:]
    argdata += args
    return funcname, func, argdata

def parse_line_data(line):
    print line
    funcname, func, argdata = parse_line(line)
    needed, varargs, _, _ = inspect.getargspec(func)
    if not needed and not varargs:
        func()
        return

    if varargs:
        needed.append(varargs)

    _validators = validators_for_function(funcname)

    # If the full input line is not valid we have to wait here until it is done
    valid, reason = line_valid(line, _validators, needed, argdata)
    while not valid:
        prompt = "{}.".format(reason)
        data = "{} {}".format(funcname, " ".join(argdata))
        line = yield prompt, data
        funcname, func, argdata = parse_line(line)
        valid, reason = line_valid(line, _validators, needed, argdata)

    neededcount = len(needed)
    wehavecount = len(argdata)
    if neededcount > wehavecount:
        prompts = list(reversed(func_args[funcname]))
        prompts = prompts[wehavecount:]
        for argindex, prompt in enumerate(prompts, start=wehavecount):
            _line = "({}) {}".format(funcname, prompt)
            data = yield _line, None
            argname = needed[argindex]
            valid, reason = data_valid(data, argname, _validators)
            while not valid:
                _line = "({}) {}. {}".format(funcname, reason, prompt)
                data = yield _line, data
                valid, reason = data_valid(data, argname, _validators)

            argdata.append(data)

    func(*argdata)

def load_from_file(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("#") or not line:
            # Comment line
            continue
        funcname, func, data = parse_line(line)
        try:
            func(*data)
        except KeyError:
            continue


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
                prompt, data = gen.send(inputdata)
        except StopIteration:
            continue


# if __name__ == "__main__":
#     runloop()

# Qt Widget
