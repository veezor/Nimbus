#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from mock import Bconsole


try:
    import bconsole
except ImportError, e:
    bconsole = Bconsole()


def test():
    global bconsole
    bconsole = Bconsole()


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
        string = string.encode("utf-8")
        return bconsole.execute_command(string)


class Command(object):

    def __init__(self, name):
        self.content = [name]

    def raw(self, string):
        self.content.append(string)
        return self

    def __getattr__(self, attr):

        content = object.__getattribute__(self, "content")
        content.append(attr)
        return self


    def get_content(self):
        return  " ".join(self.content)

    def run(self):
        txt = self.get_content()
        txt = txt.encode("utf-8")
        result = bconsole.execute_command( txt )
        self.content = []
        return result

    def __call__(self,*args):
        return self.run()

    def __getitem__(self, item):
        name = self.content[-1]
        self.content[-1] = ('%s="%s"' % (name,item))
        return self





if __name__ == "__main__":
    test()

