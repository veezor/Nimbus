#!/usr/bin/env python
# -*- coding: UTF-8 -*-



VERSION = "1.4"

from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer

import os
import shutil
import socket
import tempfile
import subprocess
from os.path import join,basename

import networkutils

import logging
import util
import _templates



class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer): 
    pass

class DaemonOperationError(Exception):
    pass

class InvalidTimeZoneError(Exception):
    pass

def _get_secure_method(instance, attr_name):
    clsname = instance.__class__.__name__
    try:
        operation, daemon = attr_name.split('_')
        if operation in instance.DAEMON_OPERATIONS and \
                daemon in instance.ALLOWED_DAEMON:
            
            def method():
                d = instance.DAEMON_MAP[daemon]
                return instance._control_daemon(d, operation)

            method.__name__ = operation + "_" + daemon
            return method

        else:
            raise AttributeError("'%s' object has no attribute '%s'" % ( 
                                  clsname, attr_name))

    except ValueError, e:
        raise AttributeError("'%s' object has no attribute '%s'" % ( 
                              clsname, attr_name))



class Manager(object):

    DAEMON_OPERATIONS = ("start", "stop", "restart", "status")

    ALLOWED_DAEMON = (  "director", "client", 
                        "storage", "networking"  )

    DAEMON_MAP = { "director" : "bacula-ctl-dir",
                   "storage" : "bacula-ctl-sd", 
                   "client" : "bacula-ctl-fd",
                   "network" : "networking" }


    def __init__(self, debug=False):

        config = util.get_config()

        self.debug=debug

        self.ip = config.get("NETWORK","address")
        self.port = config.get("NETWORK","port")
        
        self.zoneinfo = config.get("PATH",'zoneinfo')
        self.localtime = config.get("PATH", 'localtime')
        self.localtimebkp = config.get("PATH", 'localtimebkp')
        self.iftabpath = config.get("PATH","iftab")
        self.interfacespath = config.get("PATH","interfaces")
        self.dnspath = config.get("PATH","dns")
        self.logger = logging.getLogger(__name__)
        self.server = None

        if debug:
            self.logger.info('nimbusmanager started in debug mode')
            self._change_paths()

    def _change_paths(self):
        tempdir = tempfile.mkdtemp(prefix='nimbusmanager-')
        self.logger.info("Configuration file save in  %s" % tempdir)
        shutil.rmtree(tempdir)
        os.mkdir(tempdir)
        self.iftabpath = join(tempdir, basename(self.iftabpath))
        self.interfacespath = join(tempdir, basename(self.interfacespath))
        self.dnspath = join(tempdir, os.path.basename(self.dnspath))

    def generate_dns(self, ns1, ns2=None, ns3=None):
        util.make_backup(self.dnspath)
        
        ns2 = ns2 if ns2 else ns1
        ns3 = ns3 if ns3 else ns1

        dns = open(self.dnspath,"w")
        dns.write(_templates.DNS % locals())
        dns.close()
        self.logger.info("DNS file created")

    def change_timezone(self, timezone):
        self.logger.info("Attempting to change timezone to %s..." % timezone)
        self.logger.info("UCT is %s and localtime is %s." % (uct_time, local_time))
        os.rename(self.localtime, self.localtimebkp)
        tz_path = os.path.join(self.zoneinfo, timezone)
        try:
            os.link(tz_path, self.localtime)
        except OSError: # No such file or directory
            os.rename(self.localtimebkp, self.localtime)
            self.logger.info("Timezone change has failed.")
            emsg = u"Could not reach timezone file. Tried: %s" % tz_path
            raise InvalidTimeZoneError(emsg)
        os.remove(self.localtimebkp)
        os.system("hwclock --systohc")
        uct_time = util.current_time(uct=True)
        local_time = util.current_time()
        self.logger.info("Successfully changed timezone to %s!" % timezone)
        self.logger.info("UCT is %s and localtime is %s." % (uct_time, local_time))

    def generate_interfaces(self, interface_name, interface_addr=None, netmask=None, 
            type="static", broadcast=None, 
            network=None, gateway=None):

        util.make_backup(self.interfacespath)
        interfaces = open(self.interfacespath,"w")
        if type == "dhcp":
            interfaces.write(_templates.INTERFACES_DHCP % locals())
        else:
            template = _templates.INTERFACES_STATIC
            if broadcast:
                template += "broadcast %(broadcast)s\n"
            if network:
                template += "network %(network)s\n"
            if gateway:
                template += "gateway %(gateway)s\n"
            interfaces.write( template % locals())
        interfaces.close()
        self.logger.info("Interfaces file created")

    
    def get_interfaces(self):
    	return networkutils.get_interfaces()

    def _control_daemon(self, daemonname, operation):
        self.logger.info("Manager command: /etc/init.d/%s %s" % (daemonname,operation))
        if operation in self.DAEMON_OPERATIONS:
            if self.debug:
                return "debug"
            else:
                popen = subprocess.Popen( ["/etc/init.d/%s" %daemonname, 
                                          operation], 
                                          stdout=subprocess.PIPE)
                popen.wait()

                if popen.returncode != 0:
                    raise DaemonOperationError("Process returns %d", popen.returncode)

                output = popen.stdout.read()
                return output
        else:
            raise DaemonOperationError("Unknown operation: %s" % operation)


   
    def __getattr__(self, attr):
        return _get_secure_method(self, attr)



    def run(self):
        try:
            self.server = ThreadedXMLRPCServer((  self.ip, int(self.port) ), allow_none=True)
            self.server.register_instance(self)
            self.logger.info( "Inicializing NimbusManager version %s by Linconet" % VERSION )
            self.server.serve_forever()
        except socket.error, e:
            self.logger.error( "nimbusmanager not initialized." )
            raise socket.error(e)



if __name__ == "__main__":
    manager = Manager()
    manager.run()