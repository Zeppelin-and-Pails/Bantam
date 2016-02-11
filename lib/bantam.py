
from .logit import Logit
from .server.beak import Beak
import os, yaml
import tornado.web

class bantam:
    def __init__(self, config):
        self.conf = config
        log = Logit(config)
        log.info('bantam initialised')
        self.log = log
        self.conf['LOGGER'] = log

    def build(self):
        return tornado.web.Application([
            (r"(.*)", Beak, dict(config=self.conf)),
        ])

