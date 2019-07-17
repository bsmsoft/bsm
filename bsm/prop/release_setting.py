from packaging.specifiers import SpecifierSet
from packaging.specifiers import InvalidSpecifier

from bsm import BSM_VERSION

from bsm.error import PropReleaseSettingError

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.util import ensure_list

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ReleaseSetting(CommonDict):
    def __init__(self, prop):
        super(ReleaseSetting, self).__init__()

        self.__transform(prop)
        self.__expand_env(prop['scenario'], prop['attribute'])
        self.__check_bsm_version()

    def __transform(self, prop):
        param = {}
        for name in ['app', 'output', 'scenario', 'option_release',
                     'release_path', 'release_setting_origin', 'attribute']:
            param['prop_'+name] = prop[name].data_copy()

        try:
            with Handler(prop['release_path']['handler_python_dir']) as h:
                result = h.run('transform.release_setting', param)
                if isinstance(result, dict):
                    self.update(result)
        except HandlerNotFoundError as e:
            _logger.debug('Transformer for release_setting not found: %s', e)
            self.update(prop['release_setting_origin'])
        except Exception as e:
            _logger.error('Transformer for release_setting run error: %s', e)
            raise

    def __expand_env(self, prop_scenario, prop_attribute):
        format_dict = {}
        format_dict.update(prop_attribute)
        format_dict.update(prop_scenario)

        release_env = self.get('env', {})
        env_prepend_path = release_env.get('prepend_path', {})
        for k, v in env_prepend_path.items():
            result = []
            for i in ensure_list(v):
                result.append(i.format(**format_dict))
            env_prepend_path[k] = result

        env_append_path = release_env.get('append_path', {})
        for k, v in env_append_path.items():
            result = []
            for i in ensure_list(v):
                result.append(i.format(**format_dict))
            env_append_path[k] = result

        env_set_env = release_env.get('set_env', {})
        for k, v in env_set_env.items():
            env_set_env[k] = v.format(**format_dict)

        env_alias = release_env.get('alias', {})
        for k, v in env_alias.items():
            env_alias[k] = v.format(**format_dict)

    def __check_bsm_version(self):
        version_require = self.get('bsm', {}).get('require', '')
        _logger.debug('Version require: "%s"', version_require)
        if not version_require:
            return

        try:
            spec = SpecifierSet(version_require, prereleases=True)
        except InvalidSpecifier as e:
            raise PropReleaseSettingError('Require statement not valid: {0}'.format(e))

        if BSM_VERSION not in spec:
            raise PropReleaseSettingError(
                'BSM version {0} does not follow: {1}'.format(BSM_VERSION, version_require))
