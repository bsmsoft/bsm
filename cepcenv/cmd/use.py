import click

class Use(object):
    def execute(self, config, version_config, release_config, shell):
        script = ''

        manager = Manager(config, version_config, release_config)
        path, env = manager.use()

        click.echo(script, nl=False)
