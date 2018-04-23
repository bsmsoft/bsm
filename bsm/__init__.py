
BSM_HOME = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(BSM_HOME, 'BSM_VERSION'), 'r') as f:
    BSM_VERSION = f.read().strip()


class BSM(object):
    def __init__(self, app):
        self.__config_app = ConfigApp(app)
        self.__config_user = ConfigUser(self.__config_app)

    @staticmethod
    def version():
        return BSM_VERSION

    @staticmethod
    def home():
        return BSM_HOME

    def app():
        return self.__config.app.get('id', 'bsm')

    def init_script(self, shell):
        pass

    def exit_script(self, shell):
        pass

    def config(self):
        pass

    def config_user_example(self):
        pass

    def ls_remote(self):
        pass

    def install(self):
        pass

    def ls(self):
        pass

    def use(self, shell=None):
        pass

    def env(self):
        pass

    def ls_package(self):
        pass

    def default_load(self, shell=None):
        pass
