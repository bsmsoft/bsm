import os
import click


CEPCENV_HOME = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(CEPCENV_HOME, 'CEPCENV_VERSION'), 'r') as f:
    CEPCENV_VERSION = f.read().strip()


from cepcenv.cmd import Cmd


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--config', '-c', type=str, default='~/.cepcenv.conf', help='Configuration file path. Default to "~/.cepcenv.conf"')
@click.option('--shell', '-l', type=str, default='sh', help='Type of the generated shell script')
@click.option('--software-root', '-r', type=str, help='Local installed software root directory')
@click.option('--arch', type=str, help='Architecture of the machine. e.g. "x86_64"')
@click.option('--os', type=str, help='OS of the machine. e.g. "sl6"')
@click.option('--platform', type=str, help='Platform (combination of arch and os). e.g. "x86_64-sl6"')
@click.pass_context
def cli(ctx, config, verbose, shell, arch, os, platform, software_root):
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['shell_name'] = shell

    ctx.obj['arch'] = arch
    ctx.obj['os'] = os
    ctx.obj['platform'] = platform

    ctx.obj['software_root'] = software_root


@cli.command()
@click.pass_context
def version(ctx):
    '''Display version information'''
    cmd = Cmd('version')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def init(ctx):
    '''Initialize cepcenv environment'''
    cmd = Cmd('init')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def home(ctx):
    '''Display home directory of cepcenv'''
    cmd = Cmd('home')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def exit(ctx):
    '''Exit cepcenv environment completely'''
    cmd = Cmd('exit')
    cmd.execute(ctx.obj)


@cli.command()
@click.pass_context
def upgrade(ctx):
    '''Upgrade cepcenv to the latest version'''
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
@click.option('--all', '-a', is_flag=True, help='Output all of the following')
@click.option('--title', '-d', is_flag=True, help='Output title for each line')
@click.option('--arch', '-m', is_flag=True, help='Output the architecture')
@click.option('--os', '-o', is_flag=True, help='Output the OS type and version')
@click.option('--compiler', '-i', is_flag=True, help='Output the compiler type and version')
@click.option('--platform', '-p', is_flag=True, help='Output the platform')
@click.argument('version', type=str, required=False)
@click.pass_context
def platform(ctx, all, title, arch, os, compiler, platform, version):
    '''Display platform'''
    cmd = Cmd('platform')
    cmd.execute(ctx.obj, output_all=all, output_title=title, output_arch=arch, output_os=os, output_compiler=compiler,
            output_platform=platform, version_name=version)


@cli.command()
@click.option('--release-repo', '-t', type=str, help='Repository for retrieving release information')
@click.option('--release-infodir', '-i', type=str, help='Directory for retrieving release information')
@click.option('--source', '-s', type=str, help='Packages download source')
@click.option('--force', '-f', is_flag=True, help='Skip checking system requirements')
@click.option('--yes', '-y', is_flag=True, help='Install without confirmation')
@click.option('--no-clean', is_flag=True, help='Do not clean intermediate files after installation')
@click.option('--clean-only', is_flag=True, help='Clean intermediate files without installation')
@click.argument('version', type=str)
@click.pass_context
def install(ctx, release_repo, release_infodir, source, force, yes, no_clean, clean_only, version):
    '''Install specified release version'''
    cmd = Cmd('install')
    ctx.obj['release_repo'] = release_repo
    ctx.obj['release_infodir'] = release_infodir
    cmd.execute(ctx.obj, source=source, force=force, yes=yes, no_clean=no_clean, clean_only=clean_only, version_name=version)


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


def main(check_shell=False):
    cli(prog_name='cepcenv', obj={'check_shell': check_shell})
