import os
import copy

from bsm.const import BSM_HOME, BSM_VERSION

from bsm.config import Config
from bsm.env import Env
from bsm.operation import Operation

from bsm.logger import create_stream_logger
from bsm.logger import get_logger
_logger = get_logger()


class Bsm(object):
    def __init__(self, config_entry={}, initial_env=None):
        self.reload(config_entry=config_entry, initial_env=initial_env)


    def reload(self, **kwargs):
        if 'config_entry' in kwargs:
            self.__config_entry = kwargs['config_entry']

        if 'initial_env' in kwargs:
            if kwargs['initial_env'] is None:
                initial_env = os.environ
            else:
                initial_env = kwargs['initial_env']
        else:
            initial_env = self.__env.env_final()

        self.__config = Config(self.__config_entry, initial_env)

        create_stream_logger(self.__config['output']['verbose'], self.__config['output']['quiet'])

        self.__env = Env(initial_env=initial_env, env_prefix=self.__config['app']['env_prefix'])
        self.__env.load_app(self.__config['app'])

        self.__operation = Operation(self.__config, self.__env)


    def version(self):
        return BSM_VERSION

    def home(self):
        return BSM_HOME


    def app(self):
        return self.__config['app']['id']

    def config_all(self):
        return self.__config.data()

    def config(self, config_type):
        return self.__config.config(config_type)


    def ls_remote(self, list_all=False):
        return self.__operation.execute('ls_remote', list_all)

    def check_install(self):
        return self.__operation.execute('check', 'install')

    def check_runtime(self):
        return self.__operation.execute('check', 'runtime')

    def install_release(self):
        return self.__operation.execute('install-release')

    def install_package(self, category=None, subdir=None, version=None):
        return self.__operation.execute('install-package', category, subdir, version)

    def install_release_packages(self):
        return self.__operation.execute('install-release-packages')

    def ls(self):
        return self.__operation.execute('ls')

    def use(self, without_package=False):
        self.__operation.execute('load-release')
        if not without_package:
            self.__operation.execute('load-release-packages')

    def clean(self):
        self.__operation.execute('clean')

    def exit(self):
        self.__operation.execute('exit')

    def save_as_default(self):
        self.__operation.execute('save-as-default')

    def current(self):
        return self.__env.current_release()


    def ls_package(self):
        pass

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
