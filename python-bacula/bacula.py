#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import bconsole
except ImportError, e:
    print "Error: load bconsole module failed"
    test()


valid_commands = """autodisplay automount add cancel create delete label mount prune relabel release restore run setdebug status unmount update wait disable enable list llist use query reload"""



class BaculaCommandLine(object):

    connected = False
    
    def __init__(self, config="./bconsole.conf"):
        if not self.connected:
            bconsole.set_configfile(config)
            bconsole.connect()
            BaculaCommandLine.connected = True

    def __getattr__(self, name):
        if name in valid_commands:
            return Command(name)    
        else:
            return None

    def raw(self, string):
        return bconsole.execute_command(string)


class Command(object):

    def __init__(self, name):
        self.content = [name]

    def raw(self, string):
        self.content.append(name)
        return self

    def __getattr__(self, attr):

        content = object.__getattribute__(self, "content")
        content.append(attr)
        return self


    def get_content(self):
        return  " ".join(self.content)

    def run(self):
        print "DEBUG",self.get_content()
        result = bconsole.execute_command( self.get_content() )
        self.content = []
        return result

    def __call__(self,*args):
        return self.run()

    def __getitem__(self, item):
        name = self.content[-1]
        self.content[-1] = ("%s=%s" % (name,item))
        return self



def test():
    print "Using bconsole mock"
    class Bconsole(object): #Mock

        def connect(self):
            pass

        def execute_command(self, arg):
            print arg
            pass

        def set_configfile(self, filename):
            pass

        def close(self):
            pass

    global bconsole
    bconsole = Bconsole()
    cmd = BaculaCommandLine()
    cmd.status.dir["linconet-dir"].run()


if __name__ == "__main__":
    test()

