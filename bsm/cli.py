# pylint: disable=no-value-for-parameter,unexpected-keyword-arg

import click

from bsm.cmd import Cmd
from bsm.util.option import parse_lines


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode, also print debug information')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode, only print error information')
@click.option('--app-root', type=str, hidden=True, help='Application configuration directory')
@click.option('--shell', type=str, hidden=True, help='Type of shell script')
@click.option('--config-user', type=str, help='User configuration file path')
@click.option('--format', 'output_format', type=str, default='plain',
              help='Output format (json, yaml, python, plain)')
@click.option('--env', 'output_env', is_flag=True, help='Also output environment')
@click.pass_context
def cli(ctx, verbose, quiet, app_root, shell, config_user, output_format, output_env):
    if verbose:
        ctx.obj['prop_entry']['verbose'] = verbose
    if quiet:
        ctx.obj['prop_entry']['quiet'] = quiet

    if config_user is not None:
        ctx.obj['prop_entry']['config_user_file'] = config_user

    ctx.obj['output']['format'] = output_format
    ctx.obj['output']['env'] = output_env

    # app_root and shell could not be changed by arguments under shell command
    if 'app_root' not in ctx.obj['prop_entry'] or ctx.obj['prop_entry']['app_root'] is None:
        ctx.obj['prop_entry']['app_root'] = app_root
    if 'shell' not in ctx.obj['output'] or ctx.obj['output']['shell'] is None:
        ctx.obj['output']['shell'] = shell


@cli.command(name='version')
@click.pass_context
def version_cmd(ctx):
    '''Display version information'''
    Cmd.execute('version', ctx.obj)


@cli.command()
@click.pass_context
def home(ctx):
    '''Display home directory of bsm'''
    Cmd.execute('home', ctx.obj)


@cli.command()
@click.pass_context
def bsmcli(ctx):
    '''Display bsmcli path'''
    Cmd.execute('bsmcli', ctx.obj)


@cli.command()
@click.argument('shell', type=str)
@click.pass_context
def setup(ctx, shell):
    '''Get the setup script'''
    Cmd.execute('setup', ctx.obj, shell)


@cli.command()
@click.option('--no-default', is_flag=True, help='Do not load default release')
@click.option('--show-script', is_flag=True, help='Display the shell script')
@click.pass_context
def init(ctx, no_default, show_script):
    '''Initialize bsm environment'''
    ctx.obj['prop_entry']['default_scenario'] = not no_default
    Cmd.execute('init', ctx.obj, no_default,
                show_script, ctx.obj['output']['shell'])


@cli.command(name='exit')
@click.option('--show-script', is_flag=True, help='Display the shell script')
@click.pass_context
def exit_cmd(ctx, show_script):
    '''Exit bsm environment completely'''
    Cmd.execute('exit', ctx.obj, show_script, ctx.obj['output']['shell'])


@cli.command()
@click.pass_context
def upgrade(ctx):
    '''Upgrade bsm to the latest version'''
    Cmd.execute('upgrade', ctx.obj)


@cli.command()
@click.option('--version', '-n', 'scenario', type=str, help='Release version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('prop-type', type=str, required=False)
@click.argument('item-list', nargs=-1, type=str, required=False)
@click.pass_context
def prop(ctx, scenario, option, prop_type, item_list):
    '''Display prop, mostly for debug purpose'''
    ctx.obj['prop_entry']['scenario'] = scenario
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('prop', ctx.obj, prop_type, item_list)


@cli.command()
@click.option('--release-repo', '-t', type=str, help='Repository with release information')
@click.option('--all', '-a', 'list_all', is_flag=True, help='List all versions')
@click.option('--tag', '-g', is_flag=True, help='List tags')
@click.pass_context
def ls_remote(ctx, release_repo, list_all, tag):
    '''List all available release versions'''
    ctx.obj['prop_entry']['release_repo'] = release_repo
    Cmd.execute('ls-remote', ctx.obj, list_all, tag)


@cli.command()
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--installed', '-i', is_flag=True, help='List only versions installed successfully')
@click.pass_context
def ls(ctx, software_root, option, installed):
    '''List installed release versions'''
    ctx.obj['prop_entry']['software_root'] = software_root
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('ls', ctx.obj, installed)


@cli.command(name='default')
@click.pass_context
def default_cmd(ctx):
    '''List default release'''
    Cmd.execute('default', ctx.obj)


@cli.command()
@click.pass_context
def current(ctx):
    '''List current release'''
    Cmd.execute('current', ctx.obj)


@cli.command()
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--release-repo', type=str, help='Repository for retrieving release information')
@click.option('--release-source', type=str,
              help='Directory for retrieving release information. '
              'This will take precedence over "release-repo". Use this option only for development')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--reinstall', is_flag=True, help='Reinstall all packages')
@click.option('--update', is_flag=True, help='Update version information before installation')
@click.option('--without-package', is_flag=True,
              help='Do not install packages, only install the release')
@click.option('--force', '-f', is_flag=True, help='Skip checking system requirements')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.argument('version', type=str)
@click.pass_context
def install(ctx, software_root, release_repo, release_source,
            option, reinstall, update, without_package, force, yes, version):
    '''Install specified release version'''
    ctx.obj['prop_entry']['software_root'] = software_root
    ctx.obj['prop_entry']['release_repo'] = release_repo
    ctx.obj['prop_entry']['release_source'] = release_source
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    ctx.obj['prop_entry']['scenario'] = version
    ctx.obj['prop_entry']['reinstall'] = reinstall
    Cmd.execute('install', ctx.obj, update, without_package, force, yes)


@cli.command()
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--default', '-d', is_flag=True, help='Also set the version as default')
@click.option('--option', '-o', type=str, multiple=True, help='Options for the release')
@click.option('--without-package', '-p', is_flag=True, help='Do not include packages environment')
@click.argument('version', type=str)
@click.pass_context
def use(ctx, software_root, default, option, without_package, version):
    '''Switch environment to given release version'''
    ctx.obj['prop_entry']['software_root'] = software_root
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    ctx.obj['prop_entry']['scenario'] = version
    Cmd.execute('use', ctx.obj, default, without_package)


@cli.command()
@click.option('--option', '-o', type=str, multiple=True, help='Options for the release')
@click.pass_context
def refresh(ctx, option):
    '''Refresh the current release version environment'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('refresh', ctx.obj)


@cli.command()
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('command', nargs=-1, type=str, required=True)
@click.pass_context
def run(ctx, option, command):
    '''Run release command'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('run', ctx.obj, command)


@cli.command()
@click.pass_context
def clean(ctx):
    '''Clean the current release version environment'''
    Cmd.execute('clean', ctx.obj)


@cli.command()
@click.option('--all', '-a', 'list_all', is_flag=True, help='List all available packages')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_ls(ctx, list_all, option, package):
    '''List all packages of the current release versions'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-ls', ctx.obj, list_all, package)


@cli.command()
@click.option('--package-root', '-p', type=str,
              help='Package root directory for initialization, default to current directory')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.pass_context
def pkg_init(ctx, package_root, option, yes):
    '''Initialize a new package from directory'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-init', ctx.obj, package_root, yes)


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
def pkg_install(ctx, category, subdir, version,
                category_origin, subdir_origin, version_origin,
                option, reinstall, yes, package):
    '''Install specified package'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    ctx.obj['prop_entry']['reinstall'] = reinstall
    Cmd.execute('pkg-install', ctx.obj,
                category, subdir, version,
                category_origin, subdir_origin, version_origin,
                package, yes)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_use(ctx, category, subdir, version, option, package):
    '''Load a package'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-use', ctx.obj, category, subdir, version, package)


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
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-build', ctx.obj, category,
                subdir, version, rebuild, package)


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
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-remove', ctx.obj, category,
                subdir, version, force, package)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_prop(ctx, category, subdir, version, option, package):
    '''List package prop'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-prop', ctx.obj, category, subdir, version, package)


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
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-path', ctx.obj, category,
                subdir, version, list_all, package)


@cli.command()
@click.argument('package', type=str)
@click.pass_context
def pkg_clean(ctx, package):
    '''Clean a package'''
    Cmd.execute('pkg-clean', ctx.obj, package)


@cli.command()
@click.option('--category', type=str, help='Category to be installed')
@click.option('--subdir', type=str, help='Sub directory for package')
@click.option('--version', type=str, help='Package version')
@click.option('--option', '-o', type=str, multiple=True, help='Options for release')
@click.argument('package', type=str, required=False)
@click.pass_context
def pkg_edit(ctx, category, subdir, version, option, package):
    '''Edit package prop'''
    ctx.obj['prop_entry']['option'] = parse_lines(option)
    Cmd.execute('pkg-edit', ctx.obj, category, subdir, version, package)


def main(cmd_name=None, app_root=None, output_shell=None, check_cli=False):
    '''The app_root and output_shell here take precedence over cli arguments'''
    args = {}
    args['prop_entry'] = {'app_root': app_root}
    args['output'] = {'shell': output_shell}
    args['check_cli'] = check_cli

    cli(prog_name=cmd_name, obj=args)
