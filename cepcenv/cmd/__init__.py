import inspect

import click

from cepcenv.loader import load_common

from cepcenv.util import expand_path

from cepcenv.config import load_main
from cepcenv.config import load_version

from cepcenv.shell import load_shell


class CmdError(Exception):
    pass


class Cmd(object):
    def __init__(self, cmd_name):
        self.__config = {}
        self.__version_config = {}
        self.__release_config = {}
        self.__shell = None

        self.__cmd_output_shell = False
        self.__cmd_with_version = False

        self.__load_cmd(cmd_name)

    def execute(self, options_common, **kwargs):
        self.__load_config(options_common)

        if 'version_name' in kwargs:
            self.__cmd_with_version = True
            self.__version_config, self.__release_config = load_version(self.__config, kwargs['version_name'], options_common)

        self.__load_shell(options_common['shell_name'])

        if options_common['check_shell']:
            if self.__cmd_output_shell:
                click.echo('CEPCENV:OUTPUT_IS_SHELL')
            else:
                click.echo('CEPCENV:OUTPUT_IS_NOT_SHELL')
        else:
            if self.__cmd_output_shell:
                kwargs['shell'] = self.__shell
            if self.__cmd_with_version:
                del kwargs['version_name']
                kwargs['version_config'] = self.__version_config
                kwargs['release_config'] = self.__release_config
            self.__cmd.execute(config=self.__config, **kwargs)


    def __load_cmd(self, cmd_name):
        self.__cmd = None
        try:
            self.__cmd = load_common(cmd_name, 'cepcenv.cmd')()
        except Exception as e:
            raise CmdError('Can not load command "{0}": {1}'.format(cmd_name, e))

        self.__cmd_output_shell = 'shell' in inspect.getargspec(self.__cmd.execute)[0]

    def __load_config(self, options_common):
        self.__config = load_main(options_common)

    def __load_shell(self, shell_name):
        self.__shell = None
        if self.__cmd_output_shell:
            try:
                self.__shell = load_shell(shell_name)()
            except Exception as e:
                raise CmdError('Can not load shell: {0}'.format(e))
