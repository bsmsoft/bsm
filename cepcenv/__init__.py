import os
import click

from cepcenv.cmd import Cmd


CEPCENV_HOME = os.path.dirname(os.path.realpath(__file__))


@click.group()
@click.option('--config', '-c', type=str, default='~/.cepcenv.conf', help='Specify the configuration file path. Default to "~/.cepcenv.conf"')
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--shell', '-s', type=str, default='sh', help='Type of the generated shell script. Default to "sh"')
@click.option('--arch', '-m', type=str, help='Specify the architecture of the machine. e.g. "x86_64"')
@click.option('--os', '-o', type=str, help='Specify the OS of the machine. e.g. "sl6"')
@click.option('--compiler', '-i', type=str, help='Specify the compiler type and version. e.g. "gcc49"')
@click.option('--platform', '-p', type=str, help='Specify the platform (combination of arch, os and compiler). e.g. "x86_64-sl6-gcc49"')
@click.option('--release-root', '-r', type=str)
@click.option('--release-config', '-g', type=str)
@click.option('--workarea', '-w', type=str)
@click.pass_context
def cli(ctx, config, verbose, shell, arch, os, compiler, platform, release_root, release_config, workarea):
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['shell_name'] = shell

    ctx.obj['arch'] = arch
    ctx.obj['os'] = os
    ctx.obj['compiler'] = compiler
    ctx.obj['platform'] = platform

    ctx.obj['release_root'] = release_root
    ctx.obj['release_config_file'] = release_config
    ctx.obj['workarea'] = workarea


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
@click.option('--example', '-e', is_flag=True)
@click.pass_context
def config(ctx, example):
    cmd = Cmd('config')
    cmd.execute(ctx.obj, output_example=example)


@cli.command()
@click.option('--all', '-a', is_flag=True, help='Output all of the following')
@click.option('--arch', '-m', is_flag=True, help='Output the architecture')
@click.option('--os', '-o', is_flag=True, help='Output the OS type and version')
@click.option('--compiler', '-i', is_flag=True, help='Output the compiler type and version')
@click.option('--platform', '-p', is_flag=True, help='Output the platform')
@click.argument('scenario', type=str, required=False)
@click.pass_context
def platform(ctx, all, arch, os, compiler, platform, scenario):
    # Use this name to avoid conflict with python library
    cmd = Cmd('platform-cmd')
    cmd.execute(ctx.obj, output_all=all, output_arch=arch, output_os=os, output_compiler=compiler,
            output_platform=platform, scenario_name=scenario)


@cli.command()
@click.argument('scenario', type=str, required=False)
@click.pass_context
def install(ctx, scenario):
    cmd = Cmd('install')
    cmd.execute(ctx.obj, scenario_name=scenario)


@cli.command()
@click.argument('scenario', type=str, required=False)
@click.pass_context
def use(ctx, scenario):
    cmd = Cmd('use')
    cmd.execute(ctx.obj, scenario_name=scenario)


def main(check_shell=False):
    cli(prog_name='cepcenv', obj={'check_shell': check_shell})
