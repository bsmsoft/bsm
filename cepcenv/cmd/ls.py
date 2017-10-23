import os
import click

class Ls(object):
    def execute(self, config, config_version, shell):
        local_versions = []

        try:
            for version_dir in os.listdir(config_version.cepcenv_dir):
                try:
                    with open(os.path.join(config_version.cepcenv_dir, version_dir, 'def', 'config', 'version.yml')) as f:
                        version_in_def = f.read().strip()
                except:
                    continue

                if version_in_def == version_dir:
                    local_versions.append(version_in_def)
        except:
            pass

        script = ''
        for version in local_versions:
            script += shell.echo(version)

        click.echo(script, nl=False)
