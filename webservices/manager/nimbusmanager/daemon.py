#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import sys
import os
import logging

import util
import manager







def main(debug=False):
    logger = logging.getLogger(__name__)
    try:
        util.load_logging_system()
        config = util.get_config()
        pidfile = config.get("PATH","pid")
        pid = os.getpid()
        open(pidfile,'w').write("%d"%pid)

        manager.Manager(debug).run()
    except Exception, ex:
        logger.exception("Houston, we have a problem!")
