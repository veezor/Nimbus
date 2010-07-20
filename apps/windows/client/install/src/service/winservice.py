#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import bz2
import base64
import cPickle
import win32serviceutil
import win32service
import win32event
import win32api
import win32evtlogutil
import servicemanager
import subprocess

import SocketServer, socket
from time import sleep
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


TIMEOUT = 15

socket.setdefaulttimeout(TIMEOUT)

# Threaded mix-in
class AsyncXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer):
    pass


class NimbusService(object):


    def save_private_key(self, key_content):
        f =  open(r'c:\Nimbus\client.pem', 'w')
        f.write(key_content)
        f.close()
        return True
        

    def save_baculafd(self, config):
        f =  open(r'c:\"Program Files"\Bacula\bacula-fd.conf', 'w')
        f.write(key_content)
        f.close()
        return True


    def restart_bacula(self):
        cmd = subprocess.Popen(["sc","stop","Bacula-FD"])
        cmd.communicate()
        sleep(3)
        cmd = subprocess.Popen(["sc","start","Bacula-FD"])
        cmd.communicate()
        return True

    def get_home(self):
        return os.environ['HOME']

    def get_available_drives(self):
        drives = win32api.GetLogicalDrivesStrings()
        drives = drives.split('\000')[:-1]
        return drives


    def get_file_list(self):
        result = []
        walker = os.walk('c:\\')
        for directory, dirs, files in walker:
            for file in files:
                result.append( os.path.join( directory, file ))
        pickle = cPickle.dumps(result)
        compressed = bz2.compress(pickle)
        data = base64.b64encode(compressed)
        return data


    def list_dir(self, dir):
        try:
            return os.listdir(dir)
        except Exception, error:
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
        localhost = socket.gethostbyname(socket.gethostname())
        self.server = AsyncXMLRPCServer( (localhost, 17800),
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
