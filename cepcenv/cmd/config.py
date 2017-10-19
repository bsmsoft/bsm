import os
import click

from cepcenv import CEPCENV_HOME
from cepcenv.config import dump_config_str

class Config(object):
    def execute(self, config, output_example):
        if output_example:
            click.echo(self.__load_example(), nl=False)
        else:
            click.echo(dump_config_str(config), nl=False)

    def __load_example(self):
        with open(os.path.join(CEPCENV_HOME, 'support', 'cepcenv.conf.example'), 'r') as f:
            return f.read()
