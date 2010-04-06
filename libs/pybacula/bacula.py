#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from backends import get_active_backend





valid_commands = """autodisplay automount add cancel create delete label mount prune relabel release restore run setdebug status unmount update wait disable enable list llist use query reload"""


class BaculaCommandLine(object):

    connected = False
    backend = None
    
    def __init__(self, config="./bconsole.conf"):
        BaculaCommandLine.backend = get_active_backend()() # get and instantiates
        if not self.connected:
            self.backend.set_configfile(config)
            try: 
                self.backend.connect()
                BaculaCommandLine.connected = True
            except Exception, e:
                BaculaCommandLine.connected = False
                raise BConsoleInitError(e)


    def __getattr__(self, name):
        if name in valid_commands:
            return Command(name)    
        else:
            return None

    def raw(self, string):
        string = string.encode("utf-8")
        return self.backend.execute_command(string)


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
        if not self.connected:
            return False
        txt = self.get_content()
        txt = txt.encode("utf-8")
        result = BaculaCommandLine.backend.execute_command( txt )
        self.content = []
        return result

    def __call__(self,*args):
        return self.run()

    def __getitem__(self, item):
        name = self.content[-1]
        self.content[-1] = ('%s="%s"' % (name,item))
        return self





