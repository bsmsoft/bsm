from bsm.loader import run_handler
from bsm.loader import LoadError

class Selector(object):
    def __init__(self, config_user, config_version, config_release):
        self.__config_user = config_user
        self.__config_version = config_version
        self.__config_release = config_release

    def select(self, running, idle):
        param = {}
        param['config_user'] = self.__config_user
        param['config_version'] = self.__config_version.config
        param['config_release'] = self.__config_release.config
        param['running'] = running
        param['idle'] = idle

        try:
            return run_handler('selector', param)
        except LoadError as e:
            _logger.debug('Selector load failed: {0}'.format(e))
            _logger.debug('Will randomly select one')
            return [next(iter(idle))]
        except Exception as e:
            _logger.error('Selector run error: {0}'.format(e))
            raise
