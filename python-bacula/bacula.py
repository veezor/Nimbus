#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import bconsole
except ImportError, e:
    print "Error: load bconsole module failed"


def make_boolean_method(name,status):

    def meth(self):
        return bconsole.execute_command("%s %s" % (name,status))

    meth.__name__ = "%s_%s" % (name,status)
    return meth

def make_simple_method(name):

    def meth(self):
        return bconsole.execute_command(name)

    meth.__name__ = "%s" % (name,)
    return meth


def make_positional_method(name):

    def meth(self,param):
        return bconsole.execute_command(name + " " + str(param))

    meth.__name__ = "%s" % (name,)
    return meth


def make_parameterized_method(name):

    def meth(self,**kwargs):

        # TODO: special cases
        if name == "restore":
            select = kwargs.pop("select",None)

        params = " ".join( [ "%s=%s" % (x,y)  for x,y in kwargs.items()] )
        param = " ".join([name, params])

        # TODO: special cases
        if name == "run":
            param += " yes"
        elif name == "restore" and select:
            param +=  "select %s" % select
        else:
            pass

        return bconsole.execute_command(param)

    meth.__name__ = "%s" % (name,)
    return meth


def make_positional_and_parameterized_method(name):

    def meth(self,command,**kwargs):

        params = " ".join( [ "%s=%s" % (x,y)  for x,y in kwargs.items()] )
        param = " ".join([name, command,  params])
        return bconsole.execute_command(param)

    meth.__name__ = "%s" % (name,)
    return meth


class MetaCommand(type):

    def __new__(cls, name, bases, dict):

        for meth in dict['boolean_commands']:
            dict["%s_on" % meth]  = make_boolean_method(meth,"on")
            dict["%s_off" % meth]  = make_boolean_method(meth,"off")

        # FIX: refatorar
        for meth in dict['simple_commands']:
            dict["%s" % meth]  = make_simple_method(meth)

        for meth in dict['parameterized_commands']:
            dict["%s" % meth]  = make_parameterized_method(meth)

        for meth in dict['positional_commands']:
            dict["%s" % meth]  = make_positional_method(meth)

        for meth in dict['positional_and_parameterized_commands']:
            dict["%s" % meth]  = make_positional_and_parameterized_method(meth)

        return type.__new__(cls, name, bases, dict)


class BaculaCommandLine(object):

    __metaclass__ = MetaCommand

    boolean_commands = "autodisplay automount".split()
    parameterized_commands = "add cancel create delete label mount prune".split()
    parameterized_commands.extend("relabel release restore run setdebug".split())
    parameterized_commands.extend("status unmount update wait".split())
    positional_and_parameterized_commands = "disable enable list llist".split()
    positional_commands = "use ".split()
    simple_commands = "query reload".split()
    
    def __init__(self, bconfigfile=None):

        if bconfigfile:
            bconsole.set_configfile(bconfigfile)
        bconsole.connect()


    def close(self):
        bconsole.close()



def test():
    print "Using bconsole mock"
    class Bconsole(object): #Mock

        def connect(self):
            pass

        def execute_command(self, arg):
            print arg
            pass

        def close(self):
            pass

    global bconsole
    bconsole = Bconsole()
    cmd = BaculaCommandLine()
    cmd.status(dir="linconet-dir")


if __name__ == "__main__":
    test()

