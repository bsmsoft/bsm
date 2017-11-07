import os
import click

from cepcenv.logger import get_logger
_logger = get_logger()

class Ls(object):
    def execute(self, config, config_version, shell):
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

        script = ''
        for version in local_versions:
            script += shell.echo(version)

        click.echo(script, nl=False)
