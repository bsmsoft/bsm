from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Ls(Base):
    def execute(self):
        return self._bsm.ls()



        env = Env()
        current_root = env.software_root
        current_version = env.release_version

        info = Info()
        default_version_name = info.default_version
        _logger.debug('Default version name: {0}'.format(default_version_name))

        default_root = None
        default_version = None
        if default_version_name:
            config_version_default = ConfigVersion(config_user, default_version_name)
            default_root = config_version_default.get('software_root')
            default_version = config_version_default.get('version')

        _logger.debug('Current release: {0} {1}'.format(current_root, current_version))
        _logger.debug('Default release: {0} {1}'.format(default_root, default_version))


        software_root = config_version.get('software_root')
        _logger.info('(Software root: "{0}")'.format(software_root))

        for version in local_versions:
            ver_status = []
            if software_root == current_root and version == current_version:
                ver_status.append('current')
            if software_root == default_root and version == default_version:
                ver_status.append('default')

            version_line = version
            if ver_status:
                version_line += '  ({0})'.format(', '.join(ver_status))

            click.echo(version_line)
