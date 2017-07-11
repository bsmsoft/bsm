import os
import click

from cepcenv import CEPCENV_HOME

from cepcenv.shell  import load_shell

from cepcenv.loader import LoadError

def run(verbose, shell_name):
    try:
        shell = load_shell(shell_name)()
    except LoadError as e:
        raise click.BadParameter('Unknown shell "%s"' % shell_name)

    script = ''
    script += shell.set_env('CEPCENV_HOME', CEPCENV_HOME)
    script += shell.define_cepcenv()

    click.echo(script, nl=False)
