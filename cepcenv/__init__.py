import os
import click

from cepcenv.cmd import Cmd


CEPCENV_HOME = os.path.dirname(os.path.realpath(__file__))


@click.group()
@click.option('--config', '-c', type=str, default='~/.cepcenv.conf')
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--shell', '-s', type=str, default='sh')
@click.option('--arch', '-A', type=str)
@click.option('--os', '-O', type=str)
@click.option('--compiler', '-C', type=str)
@click.option('--platform', '-p', type=str)
@click.pass_context
def cli(ctx, config, verbose, shell, arch, os, compiler, platform):
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['shell_name'] = shell

    ctx.obj['arch'] = arch
    ctx.obj['os'] = os
    ctx.obj['compiler'] = compiler
    ctx.obj['platform'] = platform


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
@click.argument('scenario', type=str, required=False)
@click.pass_context
def platform(ctx, scenario):
    # Use this name to avoid conflict with python library
    cmd = Cmd('platform-cmd')
    cmd.execute(ctx.obj, scenario_name=scenario)


@cli.command()
@click.option('--example', '-e', is_flag=True)
@click.pass_context
def config(ctx, example):
    cmd = Cmd('config')
    cmd.execute(ctx.obj, output_example=example)


@cli.command()
@click.argument('scenario', type=str, required=False)
@click.pass_context
def use(ctx, scenario):
    cmd = Cmd('use')
    cmd.execute(ctx.obj, scenario_name=scenario)


@cli.command()
@click.option('--release-root', '-r', type=str)
@click.option('--release-config', '-g', type=str)
@click.argument('scenario', type=str, required=False)
@click.pass_context
def install(ctx, release_root, release_config, scenario):
    cmd = Cmd('install')
    cmd.execute(ctx.obj, scenario_name=scenario, release_root=release_root, release_config_file=release_config)


def main(check_shell=False):
    cli(prog_name='cepcenv', obj={'check_shell': check_shell})
