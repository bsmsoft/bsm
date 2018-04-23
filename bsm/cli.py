import os
import click


from bsm.cmd import Cmd
from bsm import BSM


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--app', '-a', type=str, help='Application name')
@click.option('--config-app', type=str, help='Application configuration file path')
@click.option('--config-user', type=str, help='User configuration file path')
@click.option('--shell', type=str, default='sh', help='Type of the generated shell script')
@click.option('--output-format', type=str, default='auto', help='Output format')
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.pass_context
def cli(ctx, config, verbose, shell, software_root):
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['shell_name'] = shell
    ctx.obj['software_root'] = software_root


@cli.command()
@click.pass_context
def version(ctx):
    '''Display version information'''
    cmd = Cmd('version')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def home(ctx):
    '''Display home directory of bsm'''
    cmd = Cmd('home')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def init(ctx):
    '''Initialize bsm environment'''
    cmd = Cmd('init')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def exit(ctx):
    '''Exit bsm environment completely'''
    cmd = Cmd('exit')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def upgrade(ctx):
    '''Upgrade bsm to the latest version'''
    cmd = Cmd('upgrade')
    cmd.execute(ctx.obj)


@cli.command()
@click.option('--example', '-e', is_flag=True, help='Print the configuration example')
@click.pass_context
def config(ctx, example):
    '''Display user configuration'''
    cmd = Cmd('config')
    cmd.execute(ctx.obj, output_example=example)


@cli.command(name='config-version')
@click.argument('version', type=str, required=False)
@click.pass_context
def config_version(ctx, version):
    '''Display configuration of specified release version'''
    cmd = Cmd('config_version')
    cmd.execute(ctx.obj, version_name=version)


@cli.command(name='config-release')
@click.argument('version', type=str)
@click.pass_context
def config_release(ctx, version):
    '''Display release configuration of specified release version'''
    cmd = Cmd('config_release')
    cmd.execute(ctx.obj, version_name=version)


@cli.command()
@click.option('--release-repo', '-t', type=str, help='Repository for retrieving release information')
@click.option('--release-infodir', '-i', type=str, help='Directory for retrieving release information')
@click.option('--option', '-o', type=str, multiple=True, help='Options for installation')
@click.option('--reinstall', is_flag=True, help='Reinstall all packages')
@click.option('--update', is_flag=True, help='Update version information before installation')
@click.option('--force', '-f', is_flag=True, help='Skip checking system requirements')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.argument('version', type=str)
@click.pass_context
def install(ctx, release_repo, release_infodir, option, reinstall, update, force, yes, version):
    '''Install specified release version'''
    cmd = Cmd('install')
    ctx.obj['release_repo'] = release_repo
    ctx.obj['release_infodir'] = release_infodir
    cmd.execute(ctx.obj, option_list=option, reinstall=reinstall, update=update, force=force, yes=yes, version_name=version)


@cli.command()
@click.pass_context
def ls(ctx):
    '''List installed release versions'''
    cmd = Cmd('ls')
    cmd.execute(ctx.obj)


@cli.command(name='ls-remote')
@click.option('--release-repo', '-t', type=str, help='Repository with release information')
@click.pass_context
def ls_remote(ctx, release_repo):
    '''List all available release versions'''
    cmd = Cmd('ls_remote')
    ctx.obj['release_repo'] = release_repo
    cmd.execute(ctx.obj)


@cli.command(name='ls-package')
@click.pass_context
def ls_package(ctx):
    '''List all packages of the current release versions'''
    cmd = Cmd('ls_package')
    cmd.execute(ctx.obj)


@cli.command()
@click.option('--destination', '-d', type=str, help='Directory for packing output')
@click.argument('version', type=str)
@click.pass_context
def pack(ctx, destination, version):
    '''Create tar packages for the specified release version'''
    cmd = Cmd('pack')
    cmd.execute(ctx.obj, destination=destination, version_name=version)


@cli.command()
@click.option('--default', '-d', is_flag=True, help='Also set the version as default')
@click.argument('version', type=str)
@click.pass_context
def use(ctx, default, version):
    '''Switch environment to given release version'''
    cmd = Cmd('use')
    cmd.execute(ctx.obj, default=default, version_name=version)


@cli.command()
@click.pass_context
def clean(ctx):
    '''Clean the current release version environment'''
    cmd = Cmd('clean')
    cmd.execute(ctx.obj)


def main(check_output=False):
    cli(prog_name='bsm', obj={'check_output': check_output})