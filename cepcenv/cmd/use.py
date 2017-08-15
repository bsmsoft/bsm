import click

from cepcenv.shell  import load_shell

from cepcenv.loader import LoadError


def run(verbose, shell_name, version):
    try:
        shell = load_shell(shell_name)()
    except LoadError as e:
        raise click.BadParameter('Unknown shell "{0}"'.format(shell_name))

    script = shell.set_env('CEPCSOFT_VERSION', version)

    click.echo(script, nl=False)
