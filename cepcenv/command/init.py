import os
import click

from cepcenv import CEPCENV_ROOT_DIR

def run(verbose, shell):
    shell_file = os.path.join(CEPCENV_ROOT_DIR, 'script', 'setup.'+shell)
    if not os.path.isfile(shell_file):
        click.echo('Shell "%s" init script not found' % shell, err=True)
        return 2
    click.echo(shell_file)
