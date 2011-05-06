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


import win32com.client


if win32com.client.gencache.is_readonly == True:
    win32com.client.gencache.is_readonly = False
    win32com.client.gencache.Rebuild()


import socket
import nimbusclientlib



TIMEOUT = 15

socket.setdefaulttimeout(TIMEOUT)


class XMLRPCservice(win32serviceutil.ServiceFramework):
    _svc_name_ = "NimbusService"
    _svc_display_name_ = "NimbusService"
    _svc_description_ = "Nimbus client service"

    def __init__(self, args):
        win32evtlogutil.AddSourceToRegistry( self._svc_display_name_, 
                                             sys.executable, "Application")
        win32serviceutil.ServiceFramework.__init__(self, args)
        
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server = nimbusclientlib.get_nimbus_xml_rpc_server()


                                        
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)


    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ' (%s)' % self._svc_name_))


        while win32event.WaitForSingleObject(self.hWaitStop, 0) ==\
                win32event.WAIT_TIMEOUT:
            self.server.handle_request()

        win32evtlogutil.ReportEvent( self._svc_name_,
                                     servicemanager.PYS_SERVICE_STOPPED,
                                     0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                                    (self._svc_name_,""))

                                    
                                    

    

    
def check_firewall_conf():
    check_firewall_app_conf("Nimbus Service for Windows Client", 
                            'C:\\Nimbus\\pkgs\\winservice.exe')
    check_firewall_app_conf("Nimbus Notifier for Windows Client", 
                            'C:\\Nimbus\\pkgs\\windowsnotifier.exe')
    check_firewall_app_conf("bacula-fd",
                            "C:\\Program Files\\Bacula\\bacula-fd.exe")
 
        
def check_firewall_app_conf(name, imagefile):

    firewall = win32com.client.gencache.EnsureDispatch('HNetCfg.FwMgr',0)
    allowed_apps = firewall.LocalPolicy.CurrentProfile.AuthorizedApplications
    
    service_allowed = False
    
    for app in allowed_apps:
        if app.Name == name:
            service_allowed = True
        
    if not service_allowed:
        newapp = win32com.client.Dispatch('HNetCfg.FwAuthorizedApplication')
        newapp.Name = name
        newapp.ProcessImageFileName = imagefile
        newapp.Enabled = True
        allowed_apps.Add(newapp)


check_firewall_conf()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(XMLRPCservice)
