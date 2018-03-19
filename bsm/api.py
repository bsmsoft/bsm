class BSM(object):
    def __init__(self, app):
        self.__config_app = ConfigApp(app)
        self.__config_user = ConfigUser(self.__config_app)

    def version(self):
        pass

    def home(self):
        pass

    def ls_remote(self):
        pass

    def install(self):
        pass

    def ls(self):
        pass

    def use(self):
        pass

    def env(self):
        pass

    def ls_package(self):
        pass

    def default(self):
        pass
