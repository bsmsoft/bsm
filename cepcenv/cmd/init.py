import click

from cepcenv.use import Use as CepcenvUse
from cepcenv.env import Env

from cepcenv.config.config_version import ConfigVersion
from cepcenv.config.config_release import ConfigRelease
from cepcenv.config.info import Info

from cepcenv.logger import get_logger
_logger = get_logger()

class Init(object):
    def execute(self, config, shell):
        shell.clear_script()

        shell.define_cepcenv()
        shell.newline()

        try:
            info = Info()
            default_version = info.default_version
            if default_version:
                config_version = ConfigVersion(config, default_version)
                config_release = ConfigRelease(config_version)

                obj = CepcenvUse(config, config_version, config_release)
                set_env, unset_env = obj.run()
            else:
                env = Env()
                env.clean()
                set_env, unset_env = env.env_change()

            for e in unset_env:
                shell.unset_env(e)
            for k, v in set_env.items():
                shell.set_env(k, v)
        except Exception as e:
            _logger.warn('Cat not load default version: {0}'.format(e))

        click.echo(shell.script, nl=False)
