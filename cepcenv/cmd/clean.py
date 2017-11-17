import click

from cepcenv.env import Env

class Clean(object):
    def execute(self, config, config_version, shell):
        env = Env()
        env.clean()
        setenv, unset = env.final_all_env()

        script = ''
        for e in unset:
            script += shell.unset_env(e)
        for k, v in setenv.items():
            script += shell.set_env(k, v)

        click.echo(script, nl=False)
