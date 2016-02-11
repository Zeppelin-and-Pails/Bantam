"""
logit

A custom logging library that serves mostly as a thin wrapper for logging
allows customisation via config

@category   Utility
@version    $ID: 1.1.1, 2015-07-17 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""
import logging

class Logit:
    """
    logit class, extends logging will the option to send all logging to the cli
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    max_lvl = None
    handler = None

    levels = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
             }

    def __init__(self, conf):
        """ Initialise a new logit
        :param conf: the config object
        :return logit: a new instance of a logit
        """
        self.max_lvl = conf['LOG_LEVEL']
        if self.max_lvl == 'Caveman':
            print('Caveman debug selected, printing everything')
        else:
            # setup the handler
            log_file = conf['LOG_FILE'].replace('{dir}', conf['BASE_PATH'])
            handler = logging.FileHandler(log_file)

            # set the logging level
            handler.setLevel(self.levels[self.max_lvl])

            # create a logging format
            formatter = logging.Formatter('%(asctime)s|\033[1;36m{}\033[0m-\033[1;1m%(levelname)s\033[0m: %(message)s'.format(conf['APP_NAME']))
            handler.setFormatter(formatter)

            # add the handlers to the logger
            self.logger.addHandler(handler)
            self.logger.info('Logit initialised')

    def __getattr__(self, name):
        """ Generalised function call, covers all methods
        :param name: the name of the function being called
        """
        def wrapper(*args, **kwargs):
            if self.max_lvl == 'Caveman':
                print(args[0])
            else:
                method_to_call = getattr(self.logger, name)
                method_to_call(args[0])

        return wrapper
