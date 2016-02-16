#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bantam app

Bantam CMS, a lightweight CMS built on python around a process once mentality.

@category   Utility
@version    $ID: 1.1.1, 2016-02-02 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import os, yaml
import time, sys
from lib.daemon import daemon
from lib import bantam

class BantamDaemon(daemon.Daemon):
    def __init__(self, pidfile='/tmp/bantam.pid'):
        super(BantamDaemon, self).__init__(pidfile)
        DIR = os.path.dirname(os.path.realpath(__file__))
        self.conf = yaml.safe_load(open("{}/config/bantam.cfg".format(DIR)))
        self.conf['base_path'] = DIR

    def run(self):
        engine = bantam.Bantam(self.conf)
        app = engine.build()
        app.serve()

if __name__ == "__main__":
    daemon = BantamDaemon()

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)

