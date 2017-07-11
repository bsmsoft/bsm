import os
import click


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.pass_context
def cli(ctx, verbose):
    ctx.obj['verbose'] = verbose


@cli.command()
def version():
    from cepcenv import version as cepcenv_version
    click.echo('cepcenv %s' % cepcenv_version())


@cli.command()
@click.option('--shell', '-s', type=str, default='sh')
@click.pass_context
def init(ctx, shell):
    from cepcenv.command.init import run as run_init
    run_init(verbose=ctx.obj['verbose'], shell_name=shell)


@cli.command()
@click.option('--shell', '-s', type=str, default='sh')
@click.argument('version')
@click.pass_context
def use(ctx, shell):
    from cepcenv.command.use import run as run_use
    run_use(verbose=ctx.obj['verbose'], shell_name=shell)


def main():
    cli(obj={})
