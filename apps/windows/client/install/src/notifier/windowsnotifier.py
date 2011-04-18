#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
from nimbusclientlib import Notifier
import socket


socket.setdefaulttimeout(10)




if __name__ == "__main__":
    try:
        size = len(sys.argv)
        if size == 4:
            username, password, url = sys.argv[1:]
            Notifier(username, password, url).notify()
        elif size == 5:
            username, password, url, port = sys.argv[1:]
            Notifier(username, password, url, port).notify()
        else:
            sys.exit(1)
        sys.exit(0)
    except Exception, error:
        print "error"
        sys.exit(1)
