import os

from packaging.specifiers import SpecifierSet
from packaging.specifiers import InvalidSpecifier

from bsm.config.common import Common

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.util.config import load_config
from bsm.util.config import ConfigError

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()

from bsm import BSM_VERSION

_AVAILABLE_RELEASE_CONFIG = ('version', 'setting')


class ConfigReleaseError(Exception):
    pass


def _walk_rel_dir(directory, rel_dir=''):
    if not os.path.isdir(directory):
        raise StopIteration
    res = os.listdir(directory)
    for r in res:
        full_path = os.path.join(directory, r)
        if os.path.isfile(full_path):
            yield (full_path, rel_dir, r)
            continue
        if os.path.isdir(full_path):
            new_rel_dir = os.path.join(rel_dir, r)
            for next_full_path, next_rel_dir, next_f in _walk_rel_dir(full_path, new_rel_dir):
                yield (next_full_path, next_rel_dir, next_f)


class Release(Common):
    def load(self, config_app, config_output, config_scenario, config_release_path, config_release_origin, config_attribute):
        if not ('version' in config_scenario and config_scenario['version']):
            _logger.debug('"version" not specified in config release')
            return

        self.__transform(config_app, config_output, config_scenario, config_release_path, config_release_origin, config_attribute)

        self.__expand_env(config_scenario)

        self.__check_bsm_version()

        self.__check_version_consistency(config_scenario)

    def __load_package_config(self, package_dir):
        self['package'] = {}
        for full_path, rel_dir, f in _walk_rel_dir(package_dir):
            if not f.endswith('.yml') and not f.endswith('.yaml'):
                continue
            pkg_name = os.path.splitext(f)[0]
            self['package'][os.path.join(rel_dir, pkg_name)] = load_config(full_path)

    def __transform(self, config_app, config_output, config_scenario, config_release_path, config_release_origin, config_attribute):
        param = {}
        param['config_app'] = config_app.data_copy()
        param['config_output'] = config_output.data_copy()
        param['config_scenario'] = config_scenario.data_copy()
        param['config_release_path'] = config_release_path.data_copy()
        param['config_release_origin'] = config_release_origin.data_copy()
        param['config_attribute'] = config_attribute.data_copy()

        try:
            with Handler(config_release_path['handler_python_dir']) as h:
                result = h.run('transform_release', param)
                if isinstance(result, dict):
                    self.update(result)
        except HandlerNotFoundError as e:
            _logger.debug('Transformer for release not found: {0}'.format(e))
            self.update(config_release_origin)
        except Exception as e:
            _logger.error('Transformer for release run error: {0}'.format(e))
            raise

    def __expand_env(self, config_scenario):
        release_env = self.get('setting', {}).get('env', {})
        env_prepend_path = release_env.get('prepend_path', {})
        for k, v in env_prepend_path.items():
            result = []
            for i in ensure_list(v):
                result.append(i.format(**config_scenario))
            env_prepend_path[k] = result

        env_append_path = release_env.get('append_path', {})
        for k, v in env_append_path.items():
            result = []
            for i in ensure_list(v):
                result.append(i.format(**config_scenario))
            env_append_path[k] = result

        env_set_env = release_env.get('set_env', {})
        for k, v in env_set_env.items():
            env_set_env[k] = v.format(**config_scenario)

        env_alias = release_env.get('alias', {})
        for k, v in env_alias.items():
            env_alias[k] = v.format(**config_scenario)

    def __check_bsm_version(self):
        version_require = self.get('setting', {}).get('bsm', {}).get('require', '')
        _logger.debug('Version require: "{0}"'.format(version_require))
        if not version_require:
            return

        try:
            spec = SpecifierSet(version_require, prereleases=True)
        except InvalidSpecifier as e:
            raise ConfigReleaseError('Require statement not correct: {0}'.format(e))

        if BSM_VERSION not in spec:
            raise ConfigReleaseError('BSM version "{0}" does not follow: {1}'.format(BSM_VERSION, version_require))

    def __check_version_consistency(self, config_scenario):
        version = config_scenario.get('version')
        version_in_release = self.get('version')
        if version != version_in_release:
            _logger.warn('Version inconsistency found. Request {0} but receive {1}'.format(version, version_in_release))
