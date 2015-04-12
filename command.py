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
        for prompt in prompts:
            validator = None
            # if isinstance(prompt, tuple):
            #     validator = prompt[1]
            #     prompt = prompt[0]
            _line = "({}) {}".format(funcname, prompt)
            argdata = yield _line, None

            # TODO Refactor to avoid heavy nesting
            # if validator:
            #     # Only allow input that passes the validation
            #     valid, reason = validator(argdata)
            #     while not valid:
            #         _line = "({}) {} ({}): ".format(funcname, prompt, reason)
            #         _linelength = len(_line)
            #         _line +=
            #         argdata = yield _line
            #         valid, reason = validator(argdata)
                    
            argdata.append(argdata)

    print func
    func(*argdata)

def less_then_10(value):
    if int(value) < 10:
        return True, ""
    else:
        return False, "Value must be lower then 10"

@command("What number do you want")
@check(number=less_then_10)
def valid_check(number):
    print number

        
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
            prompt, length = gen.send(None)
            while True:
                inputdata = raw_input(prompt + " ")
                print inputdata
                prompt = gen.send(inputdata)
        except StopIteration:
            continue


if __name__ == "__main__":
    runloop()

# Qt Widget
