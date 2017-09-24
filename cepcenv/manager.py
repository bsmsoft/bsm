from cepcenv.util import ensure_list

from cepcenv.install import Install

from cepcenv.use import Use


class Manager(object):
    def __init__(self, config, version_config, release_config):
        self.__config = config
        self.__version_config = version_config
        self.__release_config = release_config

    def install(self):
        obj = Install(self.__config, self.__version_config, self.__release_config)
        obj.run()

    def use(self):
        obj = Use(self.__config, self.__version_config, self.__release_config)
        return obj.run()
