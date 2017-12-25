import os
import click

from cepcenv.env import Env

from cepcenv.config.info import Info
from cepcenv.config.config_version import ConfigVersion

from cepcenv.logger import get_logger
_logger = get_logger()

class Ls(object):
    def execute(self, config, config_version):
        local_versions = []

        try:
            version_dirs = os.listdir(config_version.cepcenv_dir)
            version_dirs.sort()
            for version_dir in version_dirs:
                try:
                    with open(os.path.join(config_version.cepcenv_dir, version_dir, 'def', 'config', 'version.yml')) as f:
                        version_in_def = f.read().strip()

                    local_versions.append(version_dir)

                    if version_in_def != version_dir:
                        _logger.warn('Version inconsistent for "{0}": Defined as "{1}"'.format(version_dir, version_in_def))
                except:
                    continue
        except:
            pass


        env = Env()
        current_root = env.software_root
        current_version = env.release_version

        info = Info()
        default_version_name = info.default_version
        _logger.debug('Default version name: {0}'.format(default_version_name))

        default_root = None
        default_version = None
        if default_version_name:
            config_version_default = ConfigVersion(config, default_version_name)
            default_root = config_version_default.get('software_root')
            default_version = config_version_default.get('version')

        _logger.debug('Current release: {0} {1}'.format(current_root, current_version))
        _logger.debug('Default release: {0} {1}'.format(default_root, default_version))


        software_root = config_version.get('software_root')
        click.echo('(Software root: "{0}")'.format(software_root))

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
