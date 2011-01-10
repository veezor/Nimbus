#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import codecs
import win32serviceutil
import win32service
import win32event
import win32api
import win32evtlogutil
import servicemanager
import subprocess

import SocketServer, socket
from glob import glob
from time import sleep
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


TIMEOUT = 15

socket.setdefaulttimeout(TIMEOUT)



FDCONF = "C:\\Program Files\\Bacula\\bacula-fd.conf"
KEYPAR = "C:\\Program Files\\Bacula\\client.pem"
MASTERKEY = "C:\\Program Files\\Bacula\\master.cert"


# Threaded mix-in
class AsyncXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer):
    pass

    
    
def is_dir(name):
    if os.path.isdir(name):
        return name + "/" 
    return name

    
class NimbusService(object):

    def save_keys(self, keypar, masterkey):
        with file(KEYPAR, "w") as f:
            f.write(keypar)

        with file(MASTERKEY, "w") as f:
            f.write(masterkey)

        return True
        

    def save_config(self, config):
        with codecs.open(FDCONF, "w", "utf-8") as f:
            f.write(config)
        return True



    def restart_bacula(self):
        cmd = subprocess.Popen(["sc","stop","Bacula-FD"], 
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE )
        cmd.communicate()
        sleep(3)
        cmd = subprocess.Popen(["sc","start","Bacula-FD"], 
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE )
        cmd.communicate()
        return True
        

    def get_home(self):
        return os.environ['HOME']

    def get_available_drives(self):
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        return drives

    def list_dir(self, path):
        try:
            files = glob(os.path.join(path,'*'))
            files = map(is_dir, files)
            return files
        except IOError, error:
            return []
        

class XMLRPCservice(win32serviceutil.ServiceFramework):
    _svc_name_ = "NimbusService"
    _svc_display_name_ = "NimbusService"
    _svc_description_ = "Nimbus client service"

    def __init__(self, args):
        win32evtlogutil.AddSourceToRegistry( self._svc_display_name_, 
                                             sys.executable, "Application")
        win32serviceutil.ServiceFramework.__init__(self, args)
        
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server = AsyncXMLRPCServer( ('0.0.0.0', 11110),
                                         SimpleXMLRPCRequestHandler)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)


    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ' (%s)' % self._svc_name_))

        self.server.register_instance(NimbusService())

        while win32event.WaitForSingleObject(self.hWaitStop, 0) ==\
                win32event.WAIT_TIMEOUT:
            self.server.handle_request()

        win32evtlogutil.ReportEvent( self._svc_name_,
                                     servicemanager.PYS_SERVICE_STOPPED,
                                     0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                                    (self._svc_name_,""))

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(XMLRPCservice)
