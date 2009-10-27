#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import sys
import os
import logging

import util
import manager







def main(debug=False):
    try:
        util.load_logging_system()
        logger = logging.getLogger(__name__)

        config = util.get_config()
        pidfile = config.get("PATH","pid")
        # do the UNIX double-fork magic, see Stevens' "Advanced
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            logger.error("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")   #don't prevent unmounting....
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                open(pidfile,'w').write("%d"%pid)
                sys.exit(0)
        except OSError, e:
            logger.error("fork #2 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

        # start the daemon main loop

        manager.Manager(debug).run()
    except Exception, ex:
        logger.exception("Houston, we have a problem!")
