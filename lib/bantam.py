"""
Bantam

Bantam CMS, a lightweight CMS built on python around a process once mentality.

@category   Utility
@version    $ID: 1.1.1, 2016-02-02 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""
from .logit import Logit
from .server import beak

class Bantam:
    def __init__(self, config):
        self.conf = config
        log = Logit(config)
        log.info('bantam initialised')
        self.log = log
        self.conf['logger'] = log

    def build(self):
        return beak.Beak(self.conf)


