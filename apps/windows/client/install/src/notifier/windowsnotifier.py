#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import urllib
import urllib2
import socket


socket.setdefaulttimeout(10)



class Notifier(object):
    URL_FORMAT = "http://%s:%d/management/computers/addrequest"

    def __init__(self, address, port=80):
        self.ip = address
        self.port = int(port)


    @property
    def url(self):
        return self.URL_FORMAT % ( self.ip,
                                   self.port )

    def get_url_data(self):
        args = { "os" :  self.get_os() } 
        return urllib.urlencode( args.items() )

    def get_os(self):
        if sys.platform in "win32":
            return "WIN"
        else:
            return "UNIX"

    def run(self):
        url = urllib2.urlopen( self.url, self.get_url_data())
        data = url.read()
        url.close()


if __name__ == "__main__":
    try:
        size = len(sys.argv)
        if size == 2:
            Notifier(sys.argv[1]).run()
        elif size == 3:
            Notifier(sys.argv[1], sys.argv[2]).run()
        else:
            sys.exit(1)
        sys.exit(0)
    except Exception, error:
        print error
        sys.exit(1)
