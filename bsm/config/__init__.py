from bsm.config.app import App as ConfigApp
from bsm.config.user import User as ConfigUser
from bsm.config.release import Release as ConfigRelease
from bsm.config.package import Package as ConfigPackage

class Config(object):
    def __init__(self, config_app, config_option):
        self.__load_all(config_app, config_option)

    def __load_all(self, config_app, config_option):
        self.__config = {}
        self.__config['app'] = ConfigApp(config_app)
        self.__config['user'] = ConfigUser(app)
        self.__config['option'] = ConfigOption(app)
        self.__config['version'] = ConfigVersion(app, user)
        self.__config['release'] = ConfigRelease(app, user, version)
        self.__config['package'] = ConfigPackage(app, user, version, release)

    @property
    def config(self):
        return self.__config

    @property
    def app(self):
        return self.__config['app']

    @property
    def user(self):
        return self.__config['user']

    @property
    def release(self):
        return self.__config['release']

    @property
    def package(self, name):
        return self.__config['package'].config(name)
