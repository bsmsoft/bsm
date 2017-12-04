import click

from cepcenv.env import Env

class Exit(object):
    def execute(self, config, shell):
        script = ''

        env = Env()
        env.clean()
        set_env, unset = env.env_change()

        for e in unset:
            script += shell.unset_env(e)
        for k, v in set_env.items():
            script += shell.set_env(k, v)

        script += shell.undefine_cepcenv()

        click.echo(script, nl=False)
