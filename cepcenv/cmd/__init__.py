import inspect

import click

from cepcenv import CepcenvError

from cepcenv.loader import load_class
from cepcenv.loader import LoadError

from cepcenv.util import snake_to_camel
from cepcenv.util import expand_path

from cepcenv.config import load_config
from cepcenv.config import ConfigError

from cepcenv.shell import load_shell
from cepcenv.shell import ShellError


class CmdError(Exception):
    pass


def load_cmd(cmd_name):
    cmd_name_underscore = cmd_name.replace('-', '_')
    module_name = 'cepcenv.cmd.' + cmd_name_underscore
    class_name = snake_to_camel(cmd_name_underscore)

    try:
        c = load_class(module_name, class_name)
    except LoadError as e:
        raise CmdError('Load command "%s" error: %s' % (cmd_name, e))

    return c


class Cmd(object):
    def __init__(self, cmd_name):
        self.__load_cmd(cmd_name)

    def execute(self, param_common, **kwargs):
        self.__load_config(param_common)
        self.__load_shell(param_common)

        if param_common['check_shell']:
            if self.__cmd_output_shell:
                click.echo('CEPCENV:OUTPUT_IS_SHELL')
            else:
                click.echo('CEPCENV:OUTPUT_IS_NOT_SHELL')
        else:
            if self.__cmd_output_shell:
                self.__cmd.execute(self.__shell, **kwargs)
            else:
                self.__cmd.execute(**kwargs)


    def __load_cmd(self, cmd_name):
        self.__cmd = None
        try:
            self.__cmd = load_cmd(cmd_name)()
        except CmdError as e:
            raise CepcenvError('Can not load command: %s' % e)

        self.__cmd_output_shell = 'shell' in inspect.getargspec(self.__cmd.execute)[0]

    def __load_config(self, param_common):
        self.__config = {}

        config_file = param_common['config_file']
        if config_file:
            try:
                self.__config.update(load_config(expand_path(config_file)))
            except ConfigError as e:
                raise CepcenvError('Can not load config: %s' % e)

        # The final verbose value: self._config['verbose'] || verbose
        if ('verbose' not in self.__config) or (not self.__config['verbose']):
            self.__config['verbose'] = param_common['verbose']

    def __load_shell(self, param_common):
        self.__shell = None
        if self.__cmd_output_shell:
            try:
                self.__shell = load_shell(param_common['shell_name'])()
            except ShellError as e:
                raise CepcenvError('Can not load shell: %s' % e)
