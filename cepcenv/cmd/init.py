import click

from cepcenv.use import Use as CepcenvUse

from cepcenv.config.info import Info
from cepcenv.config.config_version import ConfigVersion
from cepcenv.config.config_release import ConfigRelease

class Init(object):
    def execute(self, config, shell):
        script = ''

        script += shell.define_cepcenv()

        info = Info()
        default_version = info.default_version
        if default_version:
            config_version = ConfigVersion(config, default_version)
            config_release = ConfigRelease(config_version)

            obj = CepcenvUse(config, config_version, config_release)
            setenv, unset = obj.run()

            for e in unset:
                script += shell.unset_env(e)
            for k, v in setenv.items():
                script += shell.set_env(k, v)

        click.echo(script, nl=False)
