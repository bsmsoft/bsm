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


    def apply_env_changes(self):
        return self.__env.apply_changes()

    def env_final(self):
        return self.__env.env_final()


    def default(self):
        return self.__config['info'].get('default', {})

    def ls_remote(self, list_all=False):
        return self.__operation.execute('ls-remote', list_all)

    def check_missing_install(self):
        return self.__operation.execute('check-missing', 'install')

    def check_missing_runtime(self):
        return self.__operation.execute('check-missing', 'runtime')

    def install_release(self):
        return self.__operation.execute('install-release')

    def install_release_packages(self):
        return self.__operation.execute('install-release-packages')

    def ls_release_version(self):
        return self.__operation.execute('ls-release-version')

    def load_release(self):
        return self.__operation.execute('load-release')

    def load_release_packages(self):
        return self.__operation.execute('load-release-packages')

    def clean(self):
        return self.__operation.execute('clean')

    def exit(self):
        return self.__operation.execute('exit')

    def save_as_default(self):
        return self.__operation.execute('save-as-default')

    def current(self):
        return self.__env.current_release()

    def detect_category(self, directory):
        return self.__operation.execute('detect-category', directory)

    def run_release_command(self, command):
        return self.__operation.execute('run-release-command', command)


    def find_package(self, package, category=None, subdir=None, version=None, from_install=False):
        return self.__operation.execute('find-package', package, category, subdir, version, from_install)

    def match_install_package(self, package, category=None, subdir=None, version=None, category_origin=None, subdir_origin=None, version_origin=None):
        return self.__operation.execute('match-install-package', package, category, subdir, version, category_origin, subdir_origin, version_origin)

    def package_path(self, package, category, subdir, version):
        return self.__operation.execute('package-path', package, category, subdir, version)

    def package_config(self, package, category, subdir, version):
        return self.__operation.execute('package-config', package, category, subdir, version)

    def package_exist(self, package, category, subdir, version):
        return self.__operation.execute('package-exist', package, category, subdir, version)

    def install_package_config(self, package, category, subdir, version, category_origin, subdir_origin, version_origin, from_install=False):
        return self.__operation.execute('install-package-config', package, category, subdir, version, category_origin, subdir_origin, version_origin, from_install)

    def install_package(self, package, category, subdir, version):
        return self.__operation.execute('install-package', package, category, subdir, version)

    def remove_package(self, package, category, subdir, version):
        return self.__operation.execute('remove-package', package, category, subdir, version)

    def detect_package_param(self, package_dir):
        return self.__operation.execute('detect-package-param', package_dir)

    def detect_package(self, directory):
        return self.__operation.execute('detect-package', directory)

    def check_conflict_package(self, directory):
        return self.__operation.execute('check-conflict-package', directory)

    def create_package_config(self, package, category, subdir, version):
        return self.__operation.execute('create-package-config', package, category, subdir, version)

    def build_package(self, package, category, subdir, version, rebuild=False):
        return self.__operation.execute('build-package', package, category, subdir, version, rebuild)

    def clean_package(self, package):
        return self.__operation.execute('clean-package', package)

    def load_package(self, package, category, subdir, version):
        return self.__operation.execute('load-package', package, category, subdir, version)

    def ls_all_package(self):
        return self.__operation.execute('ls-all-package')

    def ls_active_package(self):
        return self.__operation.execute('ls-active-package')
