from bsm.loader import run_handler

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

        return run_handler('selector', param)
