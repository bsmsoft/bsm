import os
import copy

from bsm.const import BSM_HOME, BSM_VERSION, BSMCLI_BIN

from bsm.prop import Prop
from bsm.env import Env
from bsm.operation import Operation

from bsm.logger import create_stream_logger
from bsm.logger import get_logger
_logger = get_logger()


class BSM(object):  # pylint: disable=too-many-public-methods
    def __init__(self, prop_entry=None, initial_env=None):
        self.__bsm_version = BSM_VERSION
        self.__bsm_home = BSM_HOME
        self.__bsm_cli_bin = BSMCLI_BIN

        self.__env = None

        self.reload(prop_entry=prop_entry, initial_env=initial_env)

    def reload(self, **kwargs):
        if 'prop_entry' in kwargs:
            self.__prop_entry = kwargs['prop_entry']

        if 'initial_env' in kwargs:
            if kwargs['initial_env'] is None:
                initial_env = os.environ
            else:
                initial_env = kwargs['initial_env']
        else:
            initial_env = self.__env.env_final()

        self.__prop = Prop(self.__prop_entry, initial_env)

        create_stream_logger(
            self.__prop['output']['verbose'], self.__prop['output']['quiet'])

        self.__env = Env(initial_env=initial_env,
                         env_prefix=self.__prop['app']['env_prefix'])
        self.__env.load_app(self.__prop['app'])

        self.__operation = Operation(self.__prop, self.__env)

    def version(self):
        return self.__bsm_version

    def home(self):
        return self.__bsm_home

    def cli(self):
        return self.__bsm_cli_bin

    def app(self):
        return self.__prop['app']['id']

    def prop_all(self):
        return self.__prop.data()

    def prop(self, prop_type):
        return self.__prop.prop(prop_type)

    def apply_env_changes(self):
        return self.__env.apply_changes()

    def env_final(self):
        return self.__env.env_final()

    def default(self):
        return self.__prop['info'].get('default', {})

    def ls_avail(self, list_all=False):
        return self.__operation.execute('ls-avail', list_all)

    def check_missing_install(self):
        return self.__operation.execute('check-missing', 'install')

    def check_missing_runtime(self):
        return self.__operation.execute('check-missing', 'runtime')

    def install_release(self):
        return self.__operation.execute('install-release')

    def install_release_packages(self):
        return self.__operation.execute('install-release-packages')

    def ls_release_version(self, installed=False):
        return self.__operation.execute('ls-release-version', installed)

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
        return self.__operation.execute(
            'find-package', package, category, subdir, version, from_install)

    def match_install_package(self, package,
                              category=None, subdir=None, version=None,
                              category_origin=None, subdir_origin=None, version_origin=None):
        return self.__operation.execute(
            'match-install-package', package,
            category, subdir, version,
            category_origin, subdir_origin, version_origin)

    def package_path(self, package, category, subdir, version):
        return self.__operation.execute('package-path', package, category, subdir, version)

    def package_props(self, package, category, subdir, version):
        return self.__operation.execute('package-props', package, category, subdir, version)

    def package_exist(self, package, category, subdir, version):
        return self.__operation.execute('package-exist', package, category, subdir, version)

    def install_package_prop(self, package,
                             category, subdir, version,
                             category_origin, subdir_origin, version_origin,
                             from_install=False):
        return self.__operation.execute(
            'install-package-prop', package,
            category, subdir, version,
            category_origin, subdir_origin, version_origin,
            from_install)

    def install_package(self, package, category, subdir, version):
        return self.__operation.execute('install-package', package, category, subdir, version)

    def remove_package(self, package, category, subdir, version):
        return self.__operation.execute('remove-package', package, category, subdir, version)

    def parse_package_param(self, package_dir):
        return self.__operation.execute('parse-package-param', package_dir)

    def detect_package(self, directory):
        return self.__operation.execute('detect-package', directory)

    def check_conflict_package(self, directory):
        return self.__operation.execute('check-conflict-package', directory)

    def create_package_prop(self, package, category, subdir, version):
        return self.__operation.execute('create-package-prop', package, category, subdir, version)

    def build_package(self, package, category, subdir, version, rebuild=False):
        return self.__operation.execute(
            'build-package', package, category, subdir, version, rebuild)

    def clean_package(self, package):
        return self.__operation.execute('clean-package', package)

    def load_package(self, package, category, subdir, version):
        return self.__operation.execute('load-package', package, category, subdir, version)

    def ls_all_package(self):
        return self.__operation.execute('ls-all-package')

    def ls_active_package(self):
        return self.__operation.execute('ls-active-package')
