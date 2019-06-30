import os
import click

from bsm.cmd import Cmd
from bsm.util.option import parse_lines


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode, also print debug information')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode, only print error information')
@click.option('--app-root', type=str, hidden=True, help='Application configuration directory')
@click.option('--shell', type=str, hidden=True, help='Type of shell script')
@click.option('--config-user', type=str, help='User configuration file path')
@click.option('--output-format', type=str, default='plain', help='Output format (json, yaml, python, plain)')
@click.option('--output-env', is_flag=True, help='Also output environment')
@click.pass_context
def cli(ctx, verbose, quiet, app_root, shell, config_user, output_format, output_env):
    if verbose:
        ctx.obj['config_entry']['verbose'] = verbose
    if quiet:
        ctx.obj['config_entry']['quiet'] = quiet

    if config_user is not None:
        ctx.obj['config_entry']['config_user_file'] = config_user

    ctx.obj['output']['format'] = output_format
    ctx.obj['output']['env'] = output_env

    # app_root and shell could not be changed by arguments under shell command
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
@click.argument('shell', type=str)
@click.pass_context
def setup(ctx, shell):
    '''Get the setup script'''
    cmd = Cmd()
    cmd.execute('setup', ctx.obj, shell)


@cli.command()
@click.option('--no-default', is_flag=True, help='Do not load default release')
@click.option('--show-script', is_flag=True, help='Display the shell script')
@click.pass_context
def init(ctx, no_default, show_script):
    '''Initialize bsm environment'''
    cmd = Cmd()
    ctx.obj['config_entry']['default_scenario'] = not no_default
    cmd.execute('init', ctx.obj, no_default, show_script, ctx.obj['output']['shell'])


@cli.command()
@click.option('--show-script', is_flag=True, help='Display the shell script')
@click.pass_context
def exit(ctx, show_script):
    '''Exit bsm environment completely'''
    cmd = Cmd()
    cmd.execute('exit', ctx.obj, show_script, ctx.obj['output']['shell'])


@cli.command()
@click.pass_context
def upgrade(ctx):
    '''Upgrade bsm to the latest version'''
    cmd = Cmd('upgrade')
    cmd.execute(ctx.obj)


@cli.command()
@click.option('--version', '-n', type=str, help='Release version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('config-type', type=str, required=False)
@click.argument('item-list', nargs=-1, type=str, required=False)
@click.pass_context
def config(ctx, version, option, config_type, item_list):
    '''Display configuration, mostly for debug purpose'''
    cmd = Cmd()
    ctx.obj['config_entry']['scenario'] = version
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('config', ctx.obj, config_type, item_list)


@cli.command()
@click.option('--release-repo', '-t', type=str, help='Repository with release information')
@click.option('--all', '-a', 'list_all', is_flag=True, help='List all versions')
@click.option('--tag', '-g', is_flag=True, help='List tags')
@click.pass_context
def ls_remote(ctx, release_repo, list_all, tag):
    '''List all available release versions'''
    cmd = Cmd()
    ctx.obj['release_repo'] = release_repo
    cmd.execute('ls-remote', ctx.obj, list_all, tag)


@cli.command()
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.pass_context
def ls(ctx, software_root):
    '''List installed release versions'''
    cmd = Cmd()
    ctx.obj['software_root'] = software_root
    cmd.execute('ls', ctx.obj)


@cli.command()
@click.pass_context
def default(ctx):
    '''List default release'''
    cmd = Cmd()
    cmd.execute('default', ctx.obj)


@cli.command()
@click.pass_context
def current(ctx):
    '''List current release'''
    cmd = Cmd()
    cmd.execute('current', ctx.obj)


@cli.command()
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--release-repo', type=str, help='Repository for retrieving release information')
@click.option('--release-source', type=str, help='Directory for retrieving release information. '
        'This will take precedence over "release-repo". Use this option only for development')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--reinstall', is_flag=True, help='Reinstall all packages')
@click.option('--update', is_flag=True, help='Update version information before installation')
@click.option('--without-package', is_flag=True, help='Do not install packages, only install the release')
@click.option('--force', '-f', is_flag=True, help='Skip checking system requirements')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.argument('version', type=str)
@click.pass_context
def install(ctx, software_root, release_repo, release_source, option, reinstall, update, without_package, force, yes, version):
    '''Install specified release version'''
    cmd = Cmd()
    ctx.obj['config_entry']['software_root'] = software_root
    ctx.obj['config_entry']['release_repo'] = release_repo
    ctx.obj['config_entry']['release_source'] = release_source
    ctx.obj['config_entry']['option'] = parse_lines(option)
    ctx.obj['config_entry']['scenario'] = version
    ctx.obj['config_entry']['reinstall'] = reinstall
    cmd.execute('install', ctx.obj, update, without_package, force, yes)


@cli.command()
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--default', '-d', is_flag=True, help='Also set the version as default')
@click.option('--option', '-o', type=str, multiple=True, help='Options for the release')
@click.option('--without-package', '-p', is_flag=True, help='Do not include packages environment')
@click.argument('version', type=str)
@click.pass_context
def use(ctx, software_root, default, option, without_package, version):
    '''Switch environment to given release version'''
    cmd = Cmd()
    ctx.obj['config_entry']['software_root'] = software_root
    ctx.obj['config_entry']['option'] = parse_lines(option)
    ctx.obj['config_entry']['scenario'] = version
    cmd.execute('use', ctx.obj, default, without_package)


@cli.command()
@click.option('--option', '-o', type=str, multiple=True, help='Options for the release')
@click.pass_context
def refresh(ctx, option):
    '''Refresh the current release version environment'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('refresh', ctx.obj)


@cli.command()
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('command', nargs=-1, type=str, required=True)
@click.pass_context
def run(ctx, option, command):
    '''Run release command'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('run', ctx.obj, command)


@cli.command()
@click.pass_context
def clean(ctx):
    '''Clean the current release version environment'''
    cmd = Cmd()
    cmd.execute('clean', ctx.obj)


@cli.command()
@click.option('--all', '-a', 'list_all', is_flag=True, help='List all available packages')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_ls(ctx, list_all, option, package):
    '''List all packages of the current release versions'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-ls', ctx.obj, list_all, package)


@cli.command()
@click.option('--package-root', '-p', type=str, help='Package root directory for initialization, default to current directory')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.pass_context
def pkg_init(ctx, package_root, option, yes):
    '''Initialize a new package from directory'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-init', ctx.obj, package_root, yes)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--category-origin', type=str, help='Find reference package from category')
@click.option('--subdir-origin', type=str, help='Find reference package from sub directory')
@click.option('--version-origin', type=str, help='Find reference package from package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--reinstall', is_flag=True, help='Reinstall all packages')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.argument('package', type=str)
@click.pass_context
def pkg_install(ctx, category, subdir, version, category_origin, subdir_origin, version_origin, package, option, reinstall, yes):
    '''Install specified package'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    ctx.obj['config_entry']['reinstall'] = reinstall
    cmd.execute('pkg-install', ctx.obj, category, subdir, version, category_origin, subdir_origin, version_origin, package, yes)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_use(ctx, category, subdir, version, option, package):
    '''Load a package'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-use', ctx.obj, category, subdir, version, package)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--rebuild', is_flag=True, help='Rebuild the package')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_build(ctx, category, subdir, version, option, rebuild, package):
    '''Build a package'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-build', ctx.obj, category, subdir, version, rebuild, package)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--force', '-f', is_flag=True, help='Do not prompt for confirmation')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_remove(ctx, category, subdir, version, option, force, package):
    '''Remove a package'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-remove', ctx.obj, category, subdir, version, force, package)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_config(ctx, category, subdir, version, option, package):
    '''List package config'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-config', ctx.obj, category, subdir, version, package)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--all', '-a', 'list_all', is_flag=True, help='List all available packages')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_path(ctx, category, subdir, version, option, list_all, package):
    '''List package path'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-path', ctx.obj, category, subdir, version, list_all, package)


@cli.command()
@click.argument('package', type=str)
@click.pass_context
def pkg_clean(ctx, package):
    '''Clean a package'''
    cmd = Cmd()
    cmd.execute('pkg-clean', ctx.obj, package)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_edit(ctx, category, subdir, version, option, package):
    '''Edit package configuration'''
    cmd = Cmd()
    ctx.obj['config_entry']['option'] = parse_lines(option)
    cmd.execute('pkg-edit', ctx.obj, category, subdir, version, package)


def main(cmd_name=None, app_root=None, output_shell=None, check_cli=False):
    '''The app_root and output_shell here take precedence over cli arguments'''
    cli(prog_name=cmd_name, obj={'config_entry': {'app_root': app_root}, 'output': {'shell': output_shell}, 'check_cli': check_cli})
