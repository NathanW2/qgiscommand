import re
import logger
import inspect

commands = {}

command_split = re.compile(r"[^'\s]\S*|'.+?'")


class CommandObject(object):
    def __init__(self, funcname, func, prompts=None, helptext=None,
                 validators=None, completers=None, sourcelookup=None,
                presetdata=None):
        self.func = func
        self.funcname = funcname
        self.prompts = prompts 
        self.helptext = helptext
        if not presetdata:
            presetdata = []
        self.presetdata = presetdata
        if not validators:
            self.validators = {}

        if not completers:
            self.completers = {}

        self.sourcelookup = sourcelookup

    def __iter__(self):
        needed, varargs, _, _ = inspect.getargspec(self.func)
        neededcount = len(needed)
        wehavecount = len(self.presetdata)
        if neededcount > wehavecount:
            prompts = self.prompts[wehavecount:]
            for argindex, prompt in enumerate(prompts, start=wehavecount):
                _line = "({}) {}".format(self.funcname, prompt)
                data = yield _line, None
                argname = needed[argindex]
                valid, reason = data_valid(data, argname, self.validators)
                while not valid:
                    _line = "({}) {}. {}".format(self.funcname, reason, prompt)
                    data = yield _line, data
                    valid, reason = data_valid(data, argname, self.validators)

                argdata.append(data)

    def __call__(self, *args, **kwargs):
        """
        Call the underlying function
        """
        return self.func(*args, **kwargs)
                
    def completions_for_arg(self, argname, userdata):
        try:
            completefunc = self.completers[argname]
            return completefunc(argname, userdata)
        except KeyError:
            return []


def commandlist(argname, userdata):
    return commands.keys()


def create_command_object(func):
    name = escape_name(func.__name__)
    cmdobj = CommandObject(name, func)
    commands[name] = cmdobj
    return cmdobj


def find_or_create_command_object(func):
    name = escape_name(func.__name__)
    try:
        return commands[name]
    except KeyError:
        return create_command_object(func)
        
    
class NoFunction(Exception):
    def __init__(self, message, funcname):
        super(NoFunction, self).__init__(message)
        self.funcname = funcname


def escape_name(funcname):
    funcname = funcname.replace("_", "-")
    funcname = funcname.replace(" ", "-")
    return funcname


def command(*prompts):
    (_, filename, line_number, _, _,
     _) = inspect.getouterframes(inspect.currentframe())[1]

    def wrapper(func):
        logger.msg(str(func))
        name = escape_name(func.__name__)
        promopts = list(reversed(prompts))
        helptext = inspect.getdoc(func)
        source = (filename, line_number)
        cmd = CommandObject(name, func, prompts=promopts, helptext=helptext, sourcelookup=source)
        commands[name] = cmd
        return func

    return wrapper


def check(**checks):
    def wrapper(func):
        cmdobj = find_or_create_command_object(func)
        cmdobj.validators = checks
        return func

    return wrapper


def complete_with(**functions):
    def wrapper(func):
        cmdobj = find_or_create_command_object(func)
        cmdobj.completers = functions
        return func

    return wrapper


def is_comamnd(commandname):
    if not commandname.strip():
        return False, "Function name can not be empty"
    if commandname in commands:
        return True, ''
    else:
        return False, "No command found called {}".format(commandname)


def not_empty(value):
    if not value.strip():
        return False, "Value can no be empty"
    return True, ""


@command("Alias", "Function Name", "Args")
@check(name=is_comamnd, alias=not_empty)
@complete_with(name=commandlist)
def alias(alias, name, *args):
    """
    Register a alias for a function and pre set arguments
    """
    argsstr = " ".join(args)
    args = command_split.findall(argsstr)
    name = escape_name(name)
    func = commands[name]
    cmdobj =  CommandObject(name, func, presetdata=args)
    cmdobj.helptext = "Alias for {}".format(name + args)
    commands[alias] = cmdobj


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


def validators_for_function(cmdobj):
    return cmdobj.validators


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

    data = command_split.findall(line)
    line = line.strip()
    if not data or not line:
        return

    funcname = data[0]
    try:
        cmdobj = commands[funcname]
    except KeyError:
        raise NoFunction("No command called {}".format(funcname), funcname)

    # Strip single quotes from outside of strings
    argdata = [d.strip("'") for d in data[1:]]
    cmdobj.presetdata += argdata
    return cmdobj


def parse_line_data(line):
    cmdobj = parse_line(line)
    if not needed and not varargs:
        cmdobj()

    if varargs:
        needed.append(varargs)

    _validators = cmdobj.validators

    # If the full input line is not valid we have to wait here until it is done
    # argdata = cmdobj.presetdata
    # valid, reason = line_valid(line, _validators, needed, argdata)
    # while not valid:
    #     prompt = "{}.".format(reason)
    #     data = "{} {}".format(funcname, " ".join(argdata))
    #     line = yield prompt, data
    #     funcname, func, argdata = parse_line(line)
    #     valid, reason = line_valid(line, _validators, needed, argdata)
            
    return cmdobj


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
