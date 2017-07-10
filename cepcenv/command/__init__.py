import os
import click


@click.group()
@click.option('--verbose', default=False, help='Verbose mode')
@click.pass_context
def cli(ctx, verbose):
    ctx.obj['verbose'] = verbose


@cli.command()
def version():
    from cepcenv import version as cepcenv_version
    click.echo('cepcenv %s' % cepcenv_version())


@cli.command()
@click.option('--shell', default='sh', type=str)
@click.pass_context
def init(ctx, shell):
    from cepcenv.command.init import run as init_run
    init_run(verbose=ctx.obj['verbose'], shell=shell)


def main():
    cli(obj={})

if __name__ == '__main__':
    main()
