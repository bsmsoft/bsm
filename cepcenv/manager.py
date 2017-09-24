from cepcenv.util import ensure_list

from cepcenv.install import Install


class Manager(object):
    def __init__(self, config, version_config, release_config):
        self.__config = config
        self.__version_config = version_config
        self.__release_config = release_config

    def install(self):
        install = Install(self.__config, self.__version_config, self.__release_config)

        install.run()

    def use(self):
        pass
