import os
import click

from cepcenv.cmd import Cmd


CEPCENV_HOME = os.path.dirname(os.path.realpath(__file__))


@click.group()
@click.option('--config', '-c', type=str, default='~/.cepcenv.conf', help='Configuration file path. Default to "~/.cepcenv.conf"')
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--shell', '-s', type=str, default='sh', help='Type of the generated shell script. Default to "sh"')
@click.option('--arch', '-m', type=str, help='Architecture of the machine. e.g. "x86_64"')
@click.option('--os', '-o', type=str, help='OS of the machine. e.g. "sl6"')
#@click.option('--compiler', '-l', type=str, help='Compiler type and version. e.g. "gcc49"')
@click.option('--platform', '-p', type=str, help='Platform (combination of arch and os). e.g. "x86_64-sl6"')
@click.option('--release-root', '-r', type=str)
#@click.option('--work-root', '-w', type=str)
@click.pass_context
def cli(ctx, config, verbose, shell, arch, os, platform, release_root):
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['shell_name'] = shell

    ctx.obj['arch'] = arch
    ctx.obj['os'] = os
#    ctx.obj['compiler'] = compiler
    ctx.obj['platform'] = platform

    ctx.obj['release_root'] = release_root
#    ctx.obj['work_root'] = work_root


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
def home(ctx):
    cmd = Cmd('home')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def exit(ctx):
    cmd = Cmd('exit')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def upgrade(ctx):
    cmd = Cmd('upgrade')
    cmd.execute(ctx.obj)


@cli.command()
@click.option('--example', '-e', is_flag=True)
@click.pass_context
def config(ctx, example):
    cmd = Cmd('config')
    cmd.execute(ctx.obj, output_example=example)


@cli.command(name='config-version')
@click.argument('version', type=str, required=False)
@click.pass_context
def config_version(ctx, version):
    cmd = Cmd('config_version')
    cmd.execute(ctx.obj, version_name=version)


@cli.command(name='config-release')
@click.argument('version', type=str)
@click.pass_context
def config_release(ctx, version):
    cmd = Cmd('config_release')
    cmd.execute(ctx.obj, version_name=version)


@cli.command()
@click.option('--all', '-a', is_flag=True, help='Output all of the following')
@click.option('--title', '-d', is_flag=True, help='Output title for each line')
@click.option('--arch', '-m', is_flag=True, help='Output the architecture')
@click.option('--os', '-o', is_flag=True, help='Output the OS type and version')
@click.option('--compiler', '-i', is_flag=True, help='Output the compiler type and version')
@click.option('--platform', '-p', is_flag=True, help='Output the platform')
@click.argument('version', type=str, required=False)
@click.pass_context
def platform(ctx, all, title, arch, os, compiler, platform, version):
    # Use this name to avoid conflict with python library
    cmd = Cmd('platform_cmd')
    cmd.execute(ctx.obj, output_all=all, output_title=title, output_arch=arch, output_os=os, output_compiler=compiler,
            output_platform=platform, version_name=version)


@cli.command()
@click.option('--softdef-repo', '-t', type=str)
@click.option('--softdef-dir', '-i', type=str)
@click.argument('version', type=str)
@click.pass_context
def install(ctx, softdef_repo, softdef_dir, version):
    cmd = Cmd('install')
    ctx.obj['softdef_repo'] = softdef_repo
    ctx.obj['softdef_dir'] = softdef_dir
    cmd.execute(ctx.obj, version_name=version)


@cli.command()
@click.pass_context
def ls(ctx):
    cmd = Cmd('ls')
    cmd.execute(ctx.obj)


@cli.command(name='ls-remote')
@click.option('--softdef-repo', '-t', type=str)
@click.pass_context
def ls_remote(ctx, softdef_repo):
    cmd = Cmd('ls_remote')
    ctx.obj['softdef_repo'] = softdef_repo
    cmd.execute(ctx.obj)


@cli.command()
@click.argument('version', type=str)
@click.pass_context
def use(ctx, version):
    cmd = Cmd('use')
    cmd.execute(ctx.obj, version_name=version)


def main(check_shell=False):
    cli(prog_name='cepcenv', obj={'check_shell': check_shell})
