import os
import copy

from bsm.const import BSM_HOME, BSM_VERSION

from bsm.config import Config
from bsm.env import Env
from bsm.operation import Operation

from bsm.logger import add_stream_logger
from bsm.logger import get_logger
_logger = get_logger()


class Bsm(object):
    def __init__(self, config_entry={}, initial_env=None):
        if initial_env is None:
            initial_env = os.environ

        self.__config_entry_input = config_entry
        self.__config_entry = copy.deepcopy(self.__config_entry_input)
        self.__config = Config(self.__config_entry, initial_env)

        add_stream_logger(self.__config['output']['verbose'], self.__config['output']['quiet'])

        self.__env = Env(initial_env=initial_env, env_prefix=self.__config['app']['env_prefix'])

        self.__operation = Operation(self.__config, self.__env)


    def version(self):
        return BSM_VERSION

    def home(self):
        return BSM_HOME


    def __auto_reload(method):
        def inner(self, *args, **kargs):
            self.__watch_config()
            return method(self, *args, **kargs)
        return inner

    def __watch_config(self):
        if self.__config_entry == self.__config_entry_input:
            return
        self.reload_config()


    def reload_config(self):
        self.__config_entry = copy.deepcopy(self.__config_entry_input)
        self.__config.reset(self.__config_entry)


    @property
    def entry(self):
        return self.__config_entry_input

    def switch(self, scenario):
        self.__config_entry_input['scenario'] = scenario


    @__auto_reload
    def app(self):
        return self.__config['app']['id']

    @__auto_reload
    def config_all(self):
        return self.__config.data()

    @__auto_reload
    def config(self, config_type):
        return self.__config.config(config_type)


    @__auto_reload
    def option(self):
        return self.__operation.execute('option')

    @__auto_reload
    def ls_remote(self, list_all=False):
        return self.__operation.execute('ls_remote', list_all)

    @__auto_reload
    def check_build(self):
        return self.__operation.execute('check', 'build')

    @__auto_reload
    def check_runtime(self):
        return self.__operation.execute('check', 'runtime')

    @__auto_reload
    def install_release(self):
        return self.__operation.execute('install-release')

    @__auto_reload
    def install_package(self, category=None, subdir=None, version=None):
        return self.__operation.execute('install-package', category, subdir, version)

    @__auto_reload
    def install_software(self):
        return self.__operation.execute('install-software')

    @__auto_reload
    def ls(self):
        return self.__operation.execute('ls')

    @__auto_reload
    def use(self):
        self.__operation.execute('use')

    @__auto_reload
    def ls_package(self):
        pass

    @__auto_reload
    def run_release_command(self, command, args):
        # run customized commands defined in release
        # like bsm run pack (only in current version)
        pass


    def apply_env_changes(self):
        return self.__env.apply_changes()

    def env_final(self):
        return self.__env.env_final()

    def default_version(self, shell=None):
        try:
            info = Info()
            default_version = info.default_version
            if default_version:
                config_version = ConfigVersion(config_user, default_version)
                config_release = ConfigRelease(config_version)

                obj = BsmUse(config_user, config_version, config_release)
                set_env, unset_env = obj.run()
            else:
                env = Env()
                env.clean()
                set_env, unset_env = env.env_change()

            for e in unset_env:
                shell.unset_env(e)
            for k, v in set_env.items():
                shell.set_env(k, v)
        except Exception as e:
            _logger.warn('Cat not load default version: {0}'.format(e))
