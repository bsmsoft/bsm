import os
import click

from bsm.cmd import Cmd
from bsm.util.option import parse_lines


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode, also print debug information')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode, only print error information')
#@click.option('--app', '-a', type=str, help='Application ID')
#@click.option('--config-app', type=str, help='Application configuration file path')
@click.option('--app-root', type=str, hidden=True, help='Application configuration directory')
@click.option('--shell', type=str, default='sh', hidden=True, help='Type of shell script')
@click.option('--config-user', type=str, help='User configuration file path')
@click.option('--output-format', type=str, default='plain', help='Output format')
@click.option('--output-env', is_flag=True, help='Also output environment')
@click.pass_context
def cli(ctx, verbose, quiet, app_root, shell, config_user, output_format, output_env):
    ctx.obj['config_entry']['verbose'] = verbose
    ctx.obj['config_entry']['quiet'] = quiet
    if config_user is not None:
        ctx.obj['config_entry']['config_user_file'] = config_user
    ctx.obj['output']['format'] = output_format
    ctx.obj['output']['format'] = output_format
    ctx.obj['output']['env'] = output_env

    if 'app_root' not in ctx.obj['config_entry'] or ctx.obj['config_entry']['app_root'] is None:
        ctx.obj['config_entry']['app_root'] = app_root

    if 'shell' not in ctx.obj['output'] or ctx.obj['output']['shell'] is None:
        ctx.obj['output']['shell'] = shell


@cli.command()
@click.pass_context
def version(ctx):
    '''Display version information'''
    cmd = Cmd()
    cmd.execute('version', ctx.obj)


@cli.command()
@click.pass_context
def home(ctx):
    '''Display home directory of bsm'''
    cmd = Cmd()
    cmd.execute('home', ctx.obj)


@cli.command()
@click.pass_context
def init(ctx):
    '''Initialize bsm environment'''
    cmd = Cmd()
    cmd.execute('init', ctx.obj, shell=ctx.obj['output']['shell'])


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
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--release-repo', '-t', type=str, help='Repository for retrieving release information')
@click.option('--release-source', '-i', type=str, help='Directory for retrieving release information. '
        'This will take precedence over "release-repo". Use this option only for debugging')
@click.option('--option', '-o', type=str, multiple=True, help='Options for installation')
@click.option('--reinstall', is_flag=True, help='Reinstall all packages')
@click.option('--update', is_flag=True, help='Update version information before installation')
@click.option('--force', '-f', is_flag=True, help='Skip checking system requirements')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.argument('version', type=str)
@click.pass_context
def install(ctx, software_root, release_repo, release_source, option, reinstall, update, force, yes, version):
    '''Install specified release version'''
    cmd = Cmd('install')
    ctx.obj['config_entry']['software_root'] = software_root
    ctx.obj['config_entry']['release_repo'] = release_repo
    ctx.obj['config_entry']['release_source'] = release_source
    ctx.obj['config_entry']['option'] = parse_lines(option)
    # scenario is not put in config_entry because it need to be installed
    cmd.execute(ctx.obj, scenario=version, reinstall=reinstall, update=update, force=force, yes=yes)


@cli.command()
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.pass_context
def ls(ctx, software_root):
    '''List installed release versions'''
    cmd = Cmd('ls')
    ctx.obj['software_root'] = software_root
    cmd.execute(ctx.obj)


@cli.command(name='ls-remote')
@click.option('--release-repo', '-t', type=str, help='Repository with release information')
@click.pass_context
def ls_remote(ctx, release_repo):
    '''List all available release versions'''
    cmd = Cmd()
    ctx.obj['release_repo'] = release_repo
    cmd.execute('ls-remote', ctx.obj)


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
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--default', '-d', is_flag=True, help='Also set the version as default')
@click.argument('version', type=str)
@click.pass_context
def use(ctx, software_root, default, version):
    '''Switch environment to given release version'''
    cmd = Cmd('use')
    ctx.obj['software_root'] = software_root
    cmd.execute(ctx.obj, default=default, version_name=version)


@cli.command()
@click.pass_context
def clean(ctx):
    '''Clean the current release version environment'''
    cmd = Cmd('clean')
    cmd.execute(ctx.obj)


def main(cmd_name=None, app_root=None, output_shell=None):
    cli(prog_name=cmd_name, obj={'config_entry': {'app_root': app_root}, 'output': {'shell': output_shell}})
