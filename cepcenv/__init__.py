import os
import click

from cepcenv.cmd import Cmd


CEPCENV_HOME = os.path.dirname(os.path.realpath(__file__))


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
@click.pass_context
def version(ctx):
    cmd = Cmd('version')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def init(ctx):
    cmd = Cmd('init')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def platform(ctx):
    # Use this name to avoid conflict with python library
    cmd = Cmd('platform-cmd')
    cmd.execute(ctx.obj)


@cli.command()
@click.option('--example', '-e', is_flag=True)
@click.pass_context
def config(ctx, example):
    cmd = Cmd('config')
    cmd.execute(ctx.obj, example)


@cli.command()
@click.argument('scenario', type=str)
@click.pass_context
def use(ctx, scenario):
    cmd = Cmd('use')
    cmd.execute(ctx.obj, scenario)


@cli.command()
@click.option('--release-root', '-r', type=str)
@click.option('--release-config', '-g', type=str)
@click.argument('scenario', required=False)
@click.pass_context
def install(ctx, release_root, release_config, scenario):
    cmd = Cmd('install')
    cmd.execute(ctx.obj, release_root, release_config, scenario)


def main(check_shell=False):
    cli(prog_name='cepcenv', obj={'check_shell': check_shell})
