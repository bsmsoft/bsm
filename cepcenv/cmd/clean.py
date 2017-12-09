import click

from cepcenv.env import Env

class Clean(object):
    def execute(self, config, config_version, shell):
        env = Env()
        env.clean()
        set_env, unset_env = env.env_change()

        script = ''
        for e in unset_env:
            script += shell.unset_env(e)
        for k, v in set_env.items():
            script += shell.set_env(k, v)

        click.echo(script, nl=False)
