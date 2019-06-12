from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.logger import get_logger
_logger = get_logger()


class Selector(object):
    def __init__(self, config):
        self.__config = config

    def select(self, running, idle):
        param = {}

        param['config_app'] = self.__config['app'].data_copy()
        param['config_output'] = self.__config['output'].data_copy()
        param['config_scenario'] = self.__config['scenario'].data_copy()
        param['config_release_path'] = self.__config['release_path'].data_copy()
        param['config_release'] = self.__config['release'].data_copy()
        param['config_attribute'] = self.__config['attribute'].data_copy()

        param['running'] = running
        param['idle'] = idle

        try:
            with Handler(self.__config['release_path']['handler_python_dir']) as h:
                return h.run('selector', param)
        except HandlerNotFoundError as e:
            _logger.debug('Selector not found, will randomly select one')
            return [next(iter(idle))]
        except Exception as e:
            _logger.error('Selector run error: {0}'.format(e))
            raise
