import os


BSM_HOME = os.path.dirname(os.path.realpath(__file__))

# This name is very long in order to avoid conflicts with other modules
HANDLER_MODULE_NAME = '_bsm_handler_run_avoid_conflict'


with open(os.path.join(BSM_HOME, 'VERSION'), 'r') as f:
    BSM_VERSION = f.read().strip()


from bsm.config import Config
from bsm.env import Env

from bsm.operation import Operation

from bsm.logger import add_stream_logger


def output_env():
    def inner(method):
        method()
        output_format = load(self.__config['output']['format'])
        return self.__env
    return inner


class BSM(object):
    def __init__(self, config_entry={}):
        self.__config_entry = config_entry

        self.__config = Config(self.__config_entry)

        add_stream_logger(self.__config['output']['verbose'], self.__config['output']['quiet'])

        self.__env = Env()

        self.__operation = Operation(self.__config, self.__env)


    @staticmethod
    def version():
        return BSM_VERSION

    @staticmethod
    def home():
        return BSM_HOME


    def __env_result(self):
        env_result = {}
        env_result['bsm'] = self.__env.env_all()
        env_result['final'] = self.__env.env_final()
        env_result['change'] = self.__env.env_change()
        return env_result


    def reload(self, config_entry, update_config=False):
        if update_config:
            self.__config_entry.update(config_entry)
        else:
            self.__config_entry = config_entry

        self.__config = Config(self.__config_entry)

    def app(self):
        return self.__config['app']['id']

    def init_script(self, shell):
        pass

    def exit_script(self, shell):
        pass

    def config(self, config_type, scenario=None):
        if scenario:
            self.reload({'scenario': scenario}, True)
        return dict(self.__config[config_type])

    def config_user_example(self):
        pass

    def ls_remote(self):
        return self.__operation.execute('ls_remote')

    def install(self):
        pass

    def ls(self):
        pass

    def use(self, scenario):
        self.__operation.execute('use', scenario=scenario)
        return self.__env_result()

    def env(self):
        pass

    def ls_package(self):
        pass

    def run_release_command(self, command, args):
        # run customized commands defined in release
        # like bsm run pack (only in current version)
        pass

    def default_load(self, shell=None):
        pass
