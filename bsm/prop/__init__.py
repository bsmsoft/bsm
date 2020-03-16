import os
import copy

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from bsm.util import expand_path

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.error import PropNotFoundError
from bsm.error import PropNotValidError

from bsm.prop.common_dict import CommonDict as PropCommonDict
from bsm.prop.common_list import CommonList as PropCommonList
from bsm.prop.app import App as PropApp
from bsm.prop.env import Env as PropEnv
from bsm.prop.scenario import Scenario as PropScenario
from bsm.prop.option import Option as PropOption
from bsm.prop.release_path import ReleasePath as PropReleasePath
from bsm.prop.release_version import ReleaseVersion as PropReleaseVersion
from bsm.prop.release_setting_origin import ReleaseSettingOrigin as PropReleaseSettingOrigin
from bsm.prop.release_package_origin import ReleasePackageOrigin as PropReleasePackageOrigin
from bsm.prop.release_setting import ReleaseSetting as PropReleaseSetting
from bsm.prop.release_status import ReleaseStatus as PropReleaseStatus
from bsm.prop.release_package import ReleasePackage as PropReleasePackage
from bsm.prop.category import Category as PropCategory
from bsm.prop.category_priority import CategoryPriority as PropCategoryPriority
from bsm.prop.release_install import ReleaseInstall as PropReleaseInstall
from bsm.prop.packages_runtime import PackagesRuntime as PropPackagesRuntime
from bsm.prop.packages_install import PackagesInstall as PropPackagesInstall
from bsm.prop.packages_check import PackagesCheck as PropPackagesCheck
from bsm.prop.packages_path import PackagesPath as PropPackagesPath

from bsm.logger import get_logger
_logger = get_logger()


_PROP_DEPS = {
    'entry': [],
    'app': ['entry'],
    'example': ['app'],
    'user': ['entry', 'app'],
    'output': ['entry', 'user'],
}


def _load_from_function(prop_type):
    return None


class Prop(Mapping):
    def __init__(self, prop_entry=None, initial_env=None):
        self.reset(prop_entry, initial_env)

    def reset(self, prop_entry=None, initial_env=None):
        self.__initial_env = initial_env

        if prop_entry is None and 'entry' in self:
            prop_entry = self['entry'].data()

        self.__prop = {}
        self.__prop['entry'] = PropCommonDict()
        for k, v in prop_entry.items():
            if v is not None:
                self['entry'][k] = v

    def __getitem__(self, key):
        ''' This method implements the lazy load of props
            Props are only loaded when accessed
        '''
        def method_not_found():
            raise PropNotFoundError('No such prop: {0}'.format(key))

        if key not in self.__prop:
            load_method = getattr(self, '_Prop__load_' + key, method_not_found)
            _logger.debug('Load prop: %s', key)
            self.__prop[key] = load_method()

        return self.__prop[key]

    def __iter__(self):
        return iter(self.__prop)

    def __len__(self):
        return len(self.__prop)

    def __prop_arg(self, *args):
        return {name: self[name] for name in args}

    def __load_app(self):
        return PropApp(self['entry'].get('app_root', ''))

    def __load_example(self):
        p = PropCommonDict()
        p['path'] = self['app']['example_config_user']
        try:
            with open(self['app']['example_config_user']) as f:
                p['content'] = f.read()
        except IOError as e:
            _logger.warning('Open user config example failed: %s', e)
            p['content'] = ''
        return p

    def __load_user(self):
        p = PropCommonDict()
        config_user_file = self['app']['config_user_file']
        if 'config_user_file' in self['entry']:
            config_user_file = self['entry']['config_user_file']
        p.load_from_file(expand_path(config_user_file))
        return p

    def __load_output(self):
        p = PropCommonDict()

        # verbose
        p['verbose'] = False
        if 'verbose' in self['user']:
            p['verbose'] = self['user']['verbose']
        if 'verbose' in self['entry']:
            p['verbose'] = self['entry']['verbose']

        # quiet
        p['quiet'] = False
        if 'quiet' in self['user']:
            p['quiet'] = self['user']['quiet']
        if 'quiet' in self['entry']:
            p['quiet'] = self['entry']['quiet']

        return p

    def __load_env(self):
        return PropEnv(self.__initial_env, self['app']['env_prefix'])

    def __load_info(self):
        p = PropCommonDict()
        p.load_from_file(expand_path(self['app']['bsm_info_file']))
        return p

    def __load_scenario(self):
        return PropScenario(self.__prop_arg('entry', 'app', 'info', 'env', 'user'))

    def __load_release_dir(self):
        if 'software_root' not in self['scenario']:
            raise PropNotValidError('"software_root" not specified')
        return os.path.join(self['scenario']['software_root'], self['app']['release_work_dir'])

    def __load_release_path(self):
        return PropReleasePath(self.__prop_arg('scenario', 'release_dir'))

    def __load_release_version(self):
        return PropReleaseVersion(self.__prop_arg('scenario', 'release_path')).data()

    # Release defined options, for display purpose
    def __load_option_list(self):
        p = PropCommonDict()

        if 'handler_python_dir' not in self['release_path']:
            _logger.debug('handler_python_dir not in release_path')
            return p

        try:
            with Handler(self['release_path']['handler_python_dir']) as h:
                p.update(h.run('option'))
        except HandlerNotFoundError:
            _logger.debug('Handler for option list not found')
        except Exception as e:
            _logger.error('Handler for option list run error: %s', e)
            raise

        return p

    def __load_release_option(self):
        return PropOption('attribute', self.__prop_arg(
            'entry', 'info', 'env', 'user', 'scenario', 'option_list'))

    def __load_option_attribute(self):
        return PropOption('attribute', self.__prop_arg(
            'entry', 'info', 'env', 'user', 'scenario', 'option_list'))

    def __load_option_release(self):
        return PropOption('release', self.__prop_arg(
            'entry', 'info', 'env', 'user', 'scenario', 'option_list'))

    def __load_release_setting_origin(self):
        return PropReleaseSettingOrigin(self['release_path'])

    def __load_release_package_origin(self):
        return PropReleasePackageOrigin(self['release_path'])

    def __load_attribute(self):
        p = PropCommonDict()

        if 'handler_python_dir' not in self['release_path']:
            _logger.debug('handler_python_dir not in release_path')
            return p

        param = {}
        for name in [
                'app', 'output', 'scenario', 'option_attribute',
                'release_path', 'release_setting_origin', 'release_package_origin']:
            param['prop_'+name] = self[name].data_copy()
        try:
            with Handler(self['release_path']['handler_python_dir']) as h:
                p.update(h.run('attribute', param))
        except HandlerNotFoundError:
            _logger.debug('Handler for attribute not found')
        except Exception as e:
            _logger.error('Handler for attribute run error: %s', e)
            raise

        return p

    def __load_release_setting(self):
        return PropReleaseSetting(self.__prop_arg(
            'app', 'output', 'scenario', 'option_release', 'release_path',
            'release_setting_origin', 'attribute'))

    def __load_release_package(self):
        return PropReleasePackage(self.__prop_arg(
            'app', 'output', 'scenario', 'option_release', 'release_path',
            'release_setting_origin', 'release_package_origin', 'attribute'))

    def __load_release_status(self):
        return PropReleaseStatus(self.__prop_arg(
            'release_path', 'attribute', 'release_setting'))

    def __load_category(self):
        return PropCategory(self.__prop_arg(
            'app', 'user', 'scenario', 'attribute', 'release_setting'))

    def __load_category_priority(self):
        return PropCategoryPriority(self.__prop_arg(
            'user', 'scenario', 'release_setting', 'category'))

    def __load_release_install(self):
        return PropReleaseInstall(self['release_setting'])

    def __load_packages_runtime(self):
        return PropPackagesRuntime(self.__prop_arg(
            'entry', 'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
            'release_setting', 'release_package', 'release_install',
            'category', 'category_priority'))

    def __load_packages_install(self):
        return PropPackagesInstall(self.__prop_arg(
            'entry', 'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
            'release_setting', 'release_package', 'release_install',
            'category', 'category_priority'))

    def __load_packages_check(self):
        return PropPackagesCheck(self.__prop_arg(
            'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
            'release_setting', 'release_package', 'release_install',
            'category', 'category_priority'))

    # NEED this?
    def __load_packages_runtime_path(self):
        return PropPackagesPath(self['packages_runtime'],
                                self.__prop_arg('release_path', 'category_priority'))

    # NEED this?
    def __load_packages_install_path(self):
        return PropPackagesPath(self['packages_install'],
                                self.__prop_arg('release_path', 'category_priority'))

    def prop(self, prop_type):
        if isinstance(self[prop_type],
                      (PropCommonDict, PropCommonList, PropReleaseVersion)):
            return self[prop_type].data()
        return self[prop_type]

    def prop_copy(self, prop_type):
        if isinstance(self[prop_type],
                      (PropCommonDict, PropCommonList, PropReleaseVersion)):
            return self[prop_type].data_copy()
        return copy.deepcopy(self[prop_type])

    def data(self):
        return {k: self.prop(k) for k in self}

    def data_copy(self):
        return {k: self.prop_copy(k) for k in self}
