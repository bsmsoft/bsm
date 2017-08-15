import inspect

import click

from cepcenv.error import CepcenvError

from cepcenv.loader import load_common

from cepcenv.util import expand_path

from cepcenv.config import load_config

from cepcenv.shell import load_shell


class Cmd(object):
    def __init__(self, cmd_name):
        self.__load_cmd(cmd_name)

    def execute(self, param_common, *args, **kwargs):
        self.__load_config(param_common)
        self.__load_shell(param_common)

        if param_common['check_shell']:
            if self.__cmd_output_shell:
                click.echo('CEPCENV:OUTPUT_IS_SHELL')
            else:
                click.echo('CEPCENV:OUTPUT_IS_NOT_SHELL')
        else:
            if self.__cmd_output_shell:
                self.__cmd.execute(self.__config, self.__shell, *args, **kwargs)
            else:
                self.__cmd.execute(self.__config, *args, **kwargs)


    def __load_cmd(self, cmd_name):
        self.__cmd = None
        try:
            self.__cmd = load_common(cmd_name, 'cepcenv.cmd')()
        except Exception as e:
            raise CepcenvError('Can not load command: {0}'.format(e))

        self.__cmd_output_shell = 'shell' in inspect.getargspec(self.__cmd.execute)[0]

    def __load_config(self, param_common):
        self.__config = {}

        config_file = param_common['config_file']
        if config_file:
            try:
                self.__config.update(load_config(expand_path(config_file)))
            except Exception as e:
                raise CepcenvError('Can not load config: {0}'.format(e))

        # The final verbose value: self._config['verbose'] || verbose
        if ('verbose' not in self.__config) or (not self.__config['verbose']):
            self.__config['verbose'] = param_common['verbose']

    def __load_shell(self, param_common):
        self.__shell = None
        if self.__cmd_output_shell:
            try:
                self.__shell = load_shell(param_common['shell_name'])()
            except Exception as e:
                raise CepcenvError('Can not load shell: {0}'.format(e))
