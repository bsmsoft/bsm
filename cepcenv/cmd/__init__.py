import os
import click


@click.group()
@click.option('--config', '-c', type=str, default='~/.cepcenv.conf')
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--shell', '-s', type=str, default='sh')
@click.pass_context
def cli(ctx, config, verbose, shell):
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['shell'] = shell


@cli.command()
def version():
    from cepcenv import version as cepcenv_version
    click.echo('cepcenv %s' % cepcenv_version())


@cli.command()
@click.pass_context
def init(ctx):
    from cepcenv.cmd.subcmd.init import Init
    cmd = Init(config_file=ctx.obj['config'], verbose=ctx.obj['verbose'], shell_name=ctx.obj['shell'])
    cmd.execute()


@cli.command()
@click.argument('release_version')
@click.pass_context
def use(ctx, shell, release_version):
    from cepcenv.cmd.subcmd.use import Use
    cmd = Use(config_file=ctx.obj['config'], verbose=ctx.obj['verbose'], shell_name=ctx.obj['shell'])
    cmd.execute(version=release_version)


@cli.command()
@click.argument('release_version')
@click.pass_context
def install(ctx, shell, release_version):
    from cepcenv.cmd.subcmd.install import Install
    cmd = Install(config_file=ctx.obj['config'], verbose=ctx.obj['verbose'], shell_name=ctx.obj['shell'])
    cmd.execute(version=release_version)


def main():
    cli(obj={})
