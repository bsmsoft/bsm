import os
import copy

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from bsm.util import expand_path


from bsm.config.common_dict import CommonDict as ConfigCommonDict
from bsm.config.common_list import CommonList as ConfigCommonList
from bsm.config.app import App as ConfigApp
from bsm.config.env import Env as ConfigEnv
from bsm.config.scenario import Scenario as ConfigScenario
from bsm.config.option import Option as ConfigOption
from bsm.config.release_path import ReleasePath as ConfigReleasePath
from bsm.config.release_origin import ReleaseOrigin as ConfigReleaseOrigin
from bsm.config.release_package_origin import ReleasePackageOrigin as ConfigReleasePackageOrigin
from bsm.config.release import Release as ConfigRelease
from bsm.config.release_package import ReleasePackage as ConfigReleasePackage
from bsm.config.category import Category as ConfigCategory
from bsm.config.category_priority import CategoryPriority as ConfigCategoryPriority
from bsm.config.release_install import ReleaseInstall as ConfigReleaseInstall
from bsm.config.package_runtime import PackageRuntime as ConfigPackageRuntime
from bsm.config.package_install import PackageInstall as ConfigPackageInstall
from bsm.config.package_check import PackageCheck as ConfigPackageCheck
from bsm.config.package_path import PackagePath as ConfigPackagePath

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.logger import get_logger
_logger = get_logger()


class ConfigNotValidError(Exception):
    pass


class Config(Mapping):
    def __init__(self, config_entry=None, initial_env=None):
        self.reset(config_entry, initial_env)

    def reset(self, config_entry=None, initial_env=None):
        self.__initial_env = initial_env

        if config_entry is None and 'entry' in self:
            config_entry = self['entry'].data()

        self.__config = {}
        self.__config['entry'] = ConfigCommonDict()
        for k, v in config_entry.items():
            if v is not None:
                self['entry'][k] = v


    # This method implements the lazy load of configs
    # Configs are only loaded when accessed
    def __getitem__(self, key):
        def method_not_found():
            raise ConfigNotValidError('No such config: {0}'.format(key))

        if key not in self.__config:
            load_method = getattr(self, '_Config__load_' + key, method_not_found)
            self.__config[key] = load_method()

        return self.__config[key]

    def __iter__(self):
        return iter(self.__config)

    def __len__(self):
        return len(self.__config)


    def __config_arg(self, *args):
        return {name:self[name] for name in args}


    def __load_app(self):
        return ConfigApp(self['entry'].get('app_root', ''))

    def __load_example(self):
        cfg = ConfigCommonDict()
        cfg['path'] = self['app']['example_config_user']
        try:
            with open(self['app']['example_config_user']) as f:
                cfg['content'] = f.read()
        except IOError as e:
            _logger.warning('Open user config example failed: %s', e)
            cfg['content'] = ''
        return cfg

    def __load_user(self):
        cfg = ConfigCommonDict()
        config_user_file = self['app']['config_user_file']
        if 'config_user_file' in self['entry']:
            config_user_file = self['entry']['config_user_file']
        cfg.load_from_file(expand_path(config_user_file))
        return cfg

    def __load_output(self):
        cfg = ConfigCommonDict()

        # verbose
        cfg['verbose'] = False
        if 'verbose' in self['user']:
            cfg['verbose'] = self['user']['verbose']
        if 'verbose' in self['entry']:
            cfg['verbose'] = self['entry']['verbose']

        # quiet
        cfg['quiet'] = False
        if 'quiet' in self['user']:
            cfg['quiet'] = self['user']['quiet']
        if 'quiet' in self['entry']:
            cfg['quiet'] = self['entry']['quiet']

        return cfg

    def __load_env(self):
        return ConfigEnv(self.__initial_env, self['app']['env_prefix'])

    def __load_info(self):
        cfg = ConfigCommonDict()
        cfg.load_from_file(expand_path(self['app']['config_info_file']))
        return cfg

    def __load_scenario(self):
        return ConfigScenario(self.__config_arg('entry', 'app', 'info', 'env', 'user'))

    def __load_release_dir(self):
        if 'software_root' not in self['scenario']:
            raise ConfigNotValidError('"software_root" not specified')
        return os.path.join(self['scenario']['software_root'], self['app']['release_work_dir'])

    def __load_release_path(self):
        return ConfigReleasePath(self.__config_arg('scenario', 'release_dir'))

    def __load_release_status(self):
        cfg = ConfigCommonDict()
        cfg.load_from_file(self['release_path']['status_file'])
        return cfg

    # Release defined options, for display purpose
    def __load_option_list(self):
        cfg = ConfigCommonDict()

        if 'handler_python_dir' not in self['release_path']:
            _logger.debug('handler_python_dir not in release_path')
            return cfg

        try:
            with Handler(self['release_path']['handler_python_dir']) as h:
                cfg.update(h.run('option'))
        except HandlerNotFoundError:
            _logger.debug('Handler for option list not found')
        except Exception as e:
            _logger.error('Handler for option list run error: %s', e)
            raise

        return cfg

    def __load_option(self):
        return ConfigOption(self.__config_arg(
            'entry', 'info', 'env', 'user', 'scenario', 'release_status', 'option_list'))

    def __load_release_origin(self):
        return ConfigReleaseOrigin(self.__config_arg('scenario', 'release_path'))

    def __load_release_package_origin(self):
        return ConfigReleasePackageOrigin(self['release_path'])

    def __load_attribute(self):
        cfg = ConfigCommonDict()

        if 'handler_python_dir' not in self['release_path']:
            _logger.debug('handler_python_dir not in release_path')
            return cfg

        param = {}
        for name in [
                'app', 'output', 'scenario', 'option',
                'release_path', 'release_origin', 'release_package_origin']:
            param['config_'+name] = self[name].data_copy()
        try:
            with Handler(self['release_path']['handler_python_dir']) as h:
                cfg.update(h.run('attribute', param))
        except HandlerNotFoundError:
            _logger.debug('Handler for attribute not found')
        except Exception as e:
            _logger.error('Handler for attribute run error: %s', e)
            raise

        return cfg

    def __load_release(self):
        return ConfigRelease(self.__config_arg(
            'app', 'output', 'scenario', 'option', 'release_path', 'release_origin', 'attribute'))

    def __load_release_package(self):
        return ConfigReleasePackage(self.__config_arg(
            'app', 'output', 'scenario', 'option', 'release_path',
            'release_origin', 'release_package_origin', 'attribute'))

    def __load_category(self):
        return ConfigCategory(self.__config_arg(
            'app', 'user', 'scenario', 'attribute', 'release'))

    def __load_category_priority(self):
        return ConfigCategoryPriority(self.__config_arg(
            'user', 'scenario', 'release', 'category'))

    def __load_release_install(self):
        return ConfigReleaseInstall(self['release'])

    def __load_package_runtime(self):
        return ConfigPackageRuntime(self.__config_arg(
            'entry', 'app', 'output', 'scenario', 'option', 'release_path', 'attribute',
            'release', 'release_package', 'release_install', 'category', 'category_priority'))

    def __load_package_install(self):
        return ConfigPackageInstall(self.__config_arg(
            'entry', 'app', 'output', 'scenario', 'option', 'release_path', 'attribute',
            'release', 'release_package', 'release_install', 'category', 'category_priority'))

    def __load_package_check(self):
        return ConfigPackageCheck(self.__config_arg(
            'app', 'output', 'scenario', 'option', 'release_path', 'attribute',
            'release', 'release_package', 'release_install', 'category', 'category_priority'))

    def __load_package_runtime_path(self):
        return ConfigPackagePath(self.__config_arg(
            'release_path', 'category_priority', 'package_runtime'))

    def __load_package_install_path(self):
        return ConfigPackagePath(self.__config_arg(
            'release_path', 'category_priority', 'package_install'))


    def config(self, config_type):
        if isinstance(self[config_type], (ConfigCommonDict, ConfigCommonList)):
            return self[config_type].data()
        return self[config_type]

    def config_copy(self, config_type):
        if isinstance(self[config_type], (ConfigCommonDict, ConfigCommonList)):
            return self[config_type].data_copy()
        return copy.deepcopy(self[config_type])

    def data(self):
        return {k: self.config(k) for k in self}

    def data_copy(self):
        return {k: self.config_copy(k) for k in self}
