import os
import re

from bsm.config.common import Common

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.util.config import load_config
from bsm.util.config import ConfigError

from bsm.logger import get_logger
_logger = get_logger()

from bsm import BSM_VERSION

_AVAILABLE_RELEASE_CONFIG = ('version', 'setting')


class ConfigReleaseError(Exception):
    pass


def _compare_version(ver1, ver2):
    for i in range(3):
        if len(ver1) <= i:
            c1 = -1
        else:
            c1 = ver1[i]

        if len(ver2) <= i:
            c2 = -1
        else:
            c2 = ver2[i]

        if c1 != c2:
            return c1 - c2

    return 0

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
    def load(self, config_app, config_scenario, config_release_path, config_attribute):
        if 'version' not in config_scenario or not config_scenario['version']:
            return

        self.__load_config(config_scenario, config_release_path)

        self.__transform(config_app, config_scenario, config_release_path, config_attribute)

        self.__check_bsm_version()

        self.__check_version_consistency(config_scenario)

    def __load_config(self, config_scenario, config_release_path):
        config_dir = os.path.join(config_release_path['config_dir'])
        if not os.path.isdir(config_dir):
            raise ConfigReleaseError('Release version "{0}" not found'.format(config_scenario['version']))

        for k in _AVAILABLE_RELEASE_CONFIG:
            config_file = os.path.join(config_dir, k+'.yml')
            try:
                self[k] = load_config(config_file)
            except ConfigError as e:
                _logger.warn('Fail to load config file "{0}": {1}'.format(config_file, e))

        package_dir = os.path.join(config_dir, 'package')
        self.__load_package_config(package_dir)

    def __load_package_config(self, package_dir):
        self['package'] = {}
        for full_path, rel_dir, f in _walk_rel_dir(package_dir):
            if not f.endswith('.yml') and not f.endswith('.yaml'):
                continue
            pkg_name = os.path.splitext(f)[0]
            self['package'][os.path.join(rel_dir, pkg_name)] = load_config(full_path)

    def __transform(self, config_app, config_scenario, config_release_path, config_attribute):
        param = {}
        param['config_app'] = config_app.data_copy
        param['config_scenario'] = config_scenario.data_copy
        param['config_release_path'] = config_release_path.data_copy
        param['config_release'] = self.data_copy
        param['config_attribute'] = config_attribute.data_copy

        try:
            with Handler(config_release_path['handler_python_dir']) as h:
                h.run('transform_release', param)
                if isinstance(result, dict):
                    self.clear()
                    self.update(result)
        except HandlerNotFoundError as e:
            _logger.debug('Transformer not found: {0}'.format(e))
        except Exception as e:
            _logger.error('Transformer run error: {0}'.format(e))
            raise

    def __check_bsm_version(self):
        version_require = self.get('setting', {}).get('bsm', {}).get('require', {})
        _logger.debug('Version require: {0}'.format(version_require))
        if not version_require:
            return

        m = re.match('(\d+)\.(\d+)\.(\d+)', BSM_VERSION)
        if not m:
            raise ConfigReleaseError('Can not verify bsm version: {0}'.format(BSM_VERSION))
        major, minor, patch = m.groups()
        bsm_ver_frag = [int(major), int(minor), int(patch)]

        for comp, ver in version_require.items():
            ver_frag = [int(i) for i in ver.split('.')]
            result = _compare_version(bsm_ver_frag, ver_frag)
            if comp == '<' and result >= 0 or \
                    comp == '<=' and result > 0 or \
                    comp == '=' and result != 0 or \
                    comp == '>=' and result < 0 or \
                    comp == '>' and result <= 0:
                raise ConfigReleaseError('BSM version does not follow: {0} {1} {2}'.format(BSM_VERSION, comp, ver))

    def __check_version_consistency(self, config_scenario):
        version = config_scenario.get('version')
        version_in_release = self.get('version')
        if version != version_in_release:
            _logger.warn('Version inconsistency found. Request {0} but receive {1}'.format(version, version_in_release))
