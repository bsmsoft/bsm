from cepcenv.config import load_config

class Status(object):
    def __init__(self, config_version, config_release):
        self.__config_version = config_version
        self.__config_release = config_release

    def __load_status(self):
        self.__status = load_config()

    def is_ready(self, pkg, action):
        pass

    def save_finish(self, pkg, action):
        pass
