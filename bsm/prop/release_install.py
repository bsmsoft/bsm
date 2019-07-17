from bsm.util import ensure_list

from bsm.error import PropReleaseInstallError

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ReleaseInstall(CommonDict):
    def __init__(self, prop_release_setting):
        super(ReleaseInstall, self).__init__()

        install_prop = prop_release_setting.get('install', {})

        self['steps'] = ensure_list(install_prop.get('steps', []))

        if len(self['steps']) != len(set(self['steps'])):
            raise PropReleaseInstallError('Duplicated steps found in: {0}'.format(self['steps']))
        if not self['steps']:
            _logger.warning('No install steps specified')

        self['atomic_start'] = install_prop.get('atomic_start')
        self['atomic_end'] = install_prop.get('atomic_end')

        if self['atomic_start'] not in self['steps'] or self['atomic_end'] not in self['steps']:
            raise PropReleaseInstallError(
                'Can not find atomic start/end: {0} ... {1}'
                .format(self['atomic_start'], self['atomic_end']))
        if self['steps'].index(self['atomic_start']) > self['steps'].index(self['atomic_end']):
            raise PropReleaseInstallError('atomic_start should not be after atomic_end')
