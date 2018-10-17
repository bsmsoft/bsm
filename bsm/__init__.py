import os
import copy


BSM_HOME = os.path.dirname(os.path.realpath(__file__))

# This name is very long in order to avoid conflicts with other modules
HANDLER_MODULE_NAME = '_bsm_handler_run_avoid_conflict'


with open(os.path.join(BSM_HOME, 'VERSION'), 'r') as f:
    BSM_VERSION = f.read().strip()


from bsm.config import Config
from bsm.env import Env
from bsm.operation import Operation

from bsm.logger import add_stream_logger
from bsm.logger import get_logger
_logger = get_logger()


class BSM(object):
    def __init__(self, config_entry={}):
        self.__config_entry_input = config_entry
        self.__config_entry = copy.deepcopy(self.__config_entry_input)
        self.__config = Config(self.__config_entry)

        add_stream_logger(self.__config['output']['verbose'], self.__config['output']['quiet'])

        self.__env = Env()

        self.__operation = Operation(self.__config, self.__env)


    def version(self):
        return BSM_VERSION

    def home(self):
        return BSM_HOME


    def __auto_reload(method):
        def inner(self, *args, **kargs):
            self.__reload_config()
            return method(self, *args, **kargs)
        return inner

    def __reload_config(self):
        if self.__config_entry == self.__config_entry_input:
            return
        self.__config_entry = copy.deepcopy(self.__config_entry_input)
        self.__config = Config(self.__config_entry)
        self.__operation = Operation(self.__config, self.__env)

    def __env_result(self):
        env_result = {}
        env_result['bsm'] = self.__env.env_all()
        env_result['final'] = self.__env.env_final()
        env_result['change'] = self.__env.env_change()
        return env_result


    @property
    def config_entry(self):
        return self.__config_entry_input


    def select(self, scenario):
        self.__config_entry_input['scenario'] = scenario


    @__auto_reload
    def app(self):
        return self.__config['app']['id']

    def shell_init_script(self, shell):
        return shell

    def shell_exit_script(self, shell):
        pass

    @__auto_reload
    def config_all(self):
        return self.__config

    @__auto_reload
    def config(self, config_type):
        return dict(self.__config[config_type])

    @__auto_reload
    def config_user_example(self):
        try:
            return open(self.__config['app']['example_config_user']).read()
        except Exception as e:
            _logger.warn('Open example failed: %s' % e)
            return ''


    @__auto_reload
    def ls_remote(self):
        return self.__operation.execute('ls_remote')

    @__auto_reload
    def check_compile(self):
        return self.__operation.execute('check', 'compile')

    @__auto_reload
    def check_runtime(self):
        return self.__operation.execute('check', 'runtime')

    @__auto_reload
    def install_release(self):
        return self.__operation.execute('install-release')

    @__auto_reload
    def install_software(self):
        return self.__operation.execute('install-software')

    @__auto_reload
    def ls(self):
        return self.__operation.execute('ls')

    @__auto_reload
    def use(self):
        self.__operation.execute('use')
        return self.__env_result()

    def env(self):
        return self.__env

    @__auto_reload
    def ls_package(self):
        pass

    def run_release_command(self, command, args):
        # run customized commands defined in release
        # like bsm run pack (only in current version)
        pass

    def default_load(self, shell=None):
        pass
