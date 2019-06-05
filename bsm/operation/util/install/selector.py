from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

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
            with Handler(self._config['release_path']['handler_python_dir']) as h:
                return h.run('selector', param)
        except HandlerNotFoundError:
            _logger.debug('Selector load failed: {0}'.format(e))
            _logger.debug('Will randomly select one')
            return [next(iter(idle))]
        except Exception as e:
            _logger.error('Selector run error: {0}'.format(e))
            raise

        try:
            return run_handler('selector', param)
        except LoadError as e:
            _logger.debug('Selector load failed: {0}'.format(e))
            _logger.debug('Will randomly select one')
            return [next(iter(idle))]
        except Exception as e:
            _logger.error('Selector run error: {0}'.format(e))
            raise
