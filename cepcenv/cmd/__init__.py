import inspect
import logging

import click

from cepcenv.logger import add_stream_logger
from cepcenv.loader import load_common

from cepcenv.config.main    import load_main
from cepcenv.config.config_version import ConfigVersion
from cepcenv.config.config_release import ConfigRelease

from cepcenv.shell import load_shell


class CmdError(Exception):
    pass


class Cmd(object):
    def __init__(self, cmd_name):
        self.__config = {}
        self.__config_version = {}
        self.__config_release = {}
        self.__shell = None

        self.__load_cmd(cmd_name)

    def execute(self, options_common, **kwargs):
        if options_common['check_shell']:
            if self.__cmd_output_shell:
                click.echo('CEPCENV:OUTPUT_IS_SHELL')
            else:
                click.echo('CEPCENV:OUTPUT_IS_NOT_SHELL')
            return

        self.__load_config(options_common)

        add_stream_logger('DEBUG')

        version_config_cmd = options_common.copy()
        cmd_kwargs = kwargs.copy()

        if self.__cmd_config_version or self.__cmd_config_release:
            self.__config_version = ConfigVersion(self.__config, cmd_kwargs.get('version_name'), version_config_cmd)
            if self.__cmd_config_release:
                self.__config_release = ConfigRelease(self.__config_version)
        if 'version_name' in cmd_kwargs:
            del cmd_kwargs['version_name']

        self.__load_shell(version_config_cmd['shell_name'])

        if self.__cmd_output_shell:
            cmd_kwargs['shell'] = self.__shell
        if self.__cmd_config_version:
            cmd_kwargs['config_version'] = self.__config_version
        if self.__cmd_config_release:
            cmd_kwargs['config_release'] = self.__config_release
        self.__cmd.execute(config=self.__config, **cmd_kwargs)


    def __load_cmd(self, cmd_name):
        self.__cmd = None
        try:
            self.__cmd = load_common(cmd_name, 'cepcenv.cmd')()
        except Exception as e:
            raise CmdError('Can not load command "{0}": {1}'.format(cmd_name, e))

        self.__cmd_output_shell = 'shell' in inspect.getargspec(self.__cmd.execute)[0]
        self.__cmd_config_version = 'config_version' in inspect.getargspec(self.__cmd.execute)[0]
        self.__cmd_config_release = 'config_release' in inspect.getargspec(self.__cmd.execute)[0]

    def __load_config(self, options_common):
        self.__config = load_main(options_common)

    def __load_shell(self, shell_name):
        self.__shell = None
        if self.__cmd_output_shell:
            try:
                self.__shell = load_shell(shell_name)()
            except Exception as e:
                raise CmdError('Can not load shell: {0}'.format(e))
