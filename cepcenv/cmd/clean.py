import click

from cepcenv.env import Env

class Clean(object):
    def execute(self, config, config_version, shell):
        env = Env()
        env.clean()
        set_env, unset_env = env.env_change()

        shell.clear_script()
        for e in unset_env:
            shell.unset_env(e)
        for k, v in set_env.items():
            shell.set_env(k, v)

        click.echo(shell.script, nl=False)
