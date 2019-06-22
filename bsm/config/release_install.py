from bsm.util import ensure_list

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ConfigReleaseInstallError(Exception):
    pass


class ReleaseInstall(CommonDict):
    def __init__(self, config_release):
        super(ReleaseInstall, self).__init__()

        install_cfg = config_release.get('setting', {}).get('install', {})

        self['steps'] = ensure_list(install_cfg.get('steps', []))

        if len(self['steps']) != len(set(self['steps'])):
            raise ConfigReleaseInstallError('Duplicated steps found in: {0}'.format(self['steps']))
        if len(self['steps']) == 0:
            _logger.warn('No install steps specified')

        self['atomic_start'] = install_cfg.get('atomic_start')
        self['atomic_end'] = install_cfg.get('atomic_end')

        if self['atomic_start'] not in self['steps'] or self['atomic_end'] not in self['steps']:
            raise ConfigReleaseInstallError('Can not find atomic start/end: {0} ... {1}'.format(self['atomic_start'], self['atomic_end']))
        if self['steps'].index(self['atomic_start']) > self['steps'].index(self['atomic_end']):
            raise ConfigReleaseInstallError('atomic_start should not be after atomic_end')

        self['options_to_save'] = ensure_list(install_cfg.get('options_to_save', []))
