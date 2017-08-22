import inspect

import click

from cepcenv.error import CepcenvError

from cepcenv.loader import load_common

from cepcenv.util import expand_path

from cepcenv.config import load_config

from cepcenv.shell import load_shell

from cepcenv.scenario import load_scenario


class Cmd(object):
    def __init__(self, cmd_name):
        self.__config = {}
        self.__scenario_config = {}
        self.__shell = None

        self.__cmd_output_shell = False
        self.__cmd_with_scenario = False

        self.__load_cmd(cmd_name)

    def execute(self, options_common, **kwargs):
        self.__load_config(options_common)

        if 'scenario_name' in kwargs:
            self.__cmd_with_scenario = True
            print(self.__config)
            print(kwargs)
            print(options_common)
            self.__scenario_config = load_scenario(self.__config, kwargs['scenario_name'], options_common)
            print(self.__scenario_config)

        self.__load_shell(options_common['shell_name'])

        if options_common['check_shell']:
            if self.__cmd_output_shell:
                click.echo('CEPCENV:OUTPUT_IS_SHELL')
            else:
                click.echo('CEPCENV:OUTPUT_IS_NOT_SHELL')
        else:
            if self.__cmd_output_shell:
                kwargs['shell'] = self.__shell
            if self.__cmd_with_scenario:
                del kwargs['scenario_name']
                kwargs['scenario_config'] = self.__scenario_config
            self.__cmd.execute(config=self.__config, **kwargs)


    def __load_cmd(self, cmd_name):
        self.__cmd = None
        try:
            self.__cmd = load_common(cmd_name, 'cepcenv.cmd')()
        except Exception as e:
            raise CepcenvError('Can not load command: {0}'.format(e))

        self.__cmd_output_shell = 'shell' in inspect.getargspec(self.__cmd.execute)[0]

    def __load_config(self, options_common):
        self.__config = {}

        config_file = options_common['config_file']
        if config_file:
            try:
                self.__config.update(load_config(expand_path(config_file)))
            except Exception as e:
                raise CepcenvError('Can not load config: {0}'.format(e))

        # The final verbose value: self._config['verbose'] || verbose
        if ('verbose' not in self.__config) or (not self.__config['verbose']):
            self.__config['verbose'] = options_common['verbose']

    def __load_shell(self, shell_name):
        self.__shell = None
        if self.__cmd_output_shell:
            try:
                self.__shell = load_shell(shell_name)()
            except Exception as e:
                raise CepcenvError('Can not load shell: {0}'.format(e))
