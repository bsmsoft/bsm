import os
import click


CEPCENV_HOME = os.path.dirname(os.path.realpath(__file__))


class CepcenvError(Exception):
    pass


from cepcenv.cmd import Cmd


def version():
    with open(os.path.join(CEPCENV_HOME, 'VERSION'), 'r') as f:
        ver = f.read()
    return ver.strip()


@click.group()
@click.option('--config', '-c', type=str, default='~/.cepcenv.conf')
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--shell', '-s', type=str, default='sh')
@click.pass_context
def cli(ctx, config, verbose, shell):
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['shell_name'] = shell


@cli.command()
def version():
    cmd = Cmd('version')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def platform(ctx):
    cmd = Cmd('platform-cmd')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def init(ctx):
    cmd = Cmd('init')
    cmd.execute(ctx.obj)


@cli.command()
@click.argument('release_version')
@click.pass_context
def use(ctx, release_version):
    cmd = Cmd('use')
    cmd.execute(ctx.obj, release_version=release_version)


@cli.command()
@click.argument('release_version')
@click.pass_context
def install(ctx, release_version):
    cmd = Cmd('install')
    cmd.execute(ctx.obj, release_version=release_version)


def main(check_shell=False):
    cli(prog_name='cepcenv', obj={'check_shell': check_shell})
