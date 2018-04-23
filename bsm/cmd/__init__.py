import sys
import inspect
import traceback

import click

from bsm.logger import add_stream_logger
from bsm.logger import get_logger

from bsm.loader import load_common

from bsm.config.user import load_config_user
from bsm.config.config_version import ConfigVersion
from bsm.config.config_release import ConfigRelease
from bsm.config.config_release import ConfigReleaseError

from bsm.util.option import parse_lines

from bsm.shell import Shell


_logger = get_logger()


class CmdError(Exception):
    pass


class Cmd(object):
    def __init__(self, cmd_name):
        self.__config_user = {}

        self.__load_cmd(cmd_name)

    def execute(self, options_common, **kwargs):
        if 'check_shell' in options_common and options_common['check_shell']:
            if self.__cmd_output_shell:
                click.echo('BSM:OUTPUT_IS_SHELL')
            else:
                click.echo('BSM:OUTPUT_IS_NOT_SHELL')
            return

        self.__load_config(options_common)

        add_stream_logger(self.__config_user['verbose'])

        version_cmd = options_common.copy()
        cmd_kwargs = kwargs.copy()

        try:
            self.__execute_main(version_cmd, cmd_kwargs)
        except ConfigReleaseError as e:
            _logger.error(str(e))
            _logger.critical('Can not load release version: {0}'.format(cmd_kwargs.get('version_name')))
            sys.exit(2)
        except Exception as e:
            _logger.critical('Fatal error ({0}): {1}'.format(type(e).__name__, e))
            if self.__config_user['verbose']:
                _logger.critical('\n{0}'.format(traceback.format_exc()))
            sys.exit(1)


    def __execute_main(self, version_cmd, cmd_kwargs):
        option_release = {}
        if 'option_list' in cmd_kwargs:
            option_release = parse_lines(cmd_kwargs['option_list'])
            del cmd_kwargs['option_list']

        config_version = None
        config_release = None
        if self.__cmd_config_version or self.__cmd_config_release:
            config_version = ConfigVersion(self.__config_user, cmd_kwargs.get('version_name'), version_cmd)

            if self.__cmd_config_release:
                config_release = ConfigRelease(self.__config_user, config_version, option_release)

                extra_config = config_release.get('setting', {}).get('extra_config', [])
                if extra_config:
                    config_version = ConfigVersion(self.__config_user, cmd_kwargs.get('version_name'), version_cmd, extra_config)

        if 'version_name' in cmd_kwargs:
            del cmd_kwargs['version_name']

        if self.__cmd_output_shell:
            cmd_kwargs['shell'] = self.__load_shell(version_cmd['shell_name'])
        if self.__cmd_config_user:
            cmd_kwargs['config_user'] = self.__config_user
        if self.__cmd_config_version:
            cmd_kwargs['config_version'] = config_version
        if self.__cmd_config_release:
            cmd_kwargs['config_release'] = config_release
        if self.__cmd_option:
            cmd_kwargs['option'] = option_release

        self.__cmd.execute(**cmd_kwargs)

    def __load_cmd(self, cmd_name):
        self.__cmd = None
        try:
            self.__cmd = load_common(cmd_name, 'bsm.cmd')()
        except Exception as e:
            raise CmdError('Can not load command "{0}": {1}'.format(cmd_name, e))

        self.__cmd_output_shell = 'shell' in inspect.getargspec(self.__cmd.execute)[0]
        self.__cmd_config_user = 'config_user' in inspect.getargspec(self.__cmd.execute)[0]
        self.__cmd_config_version = 'config_version' in inspect.getargspec(self.__cmd.execute)[0]
        self.__cmd_config_release = 'config_release' in inspect.getargspec(self.__cmd.execute)[0]
        self.__cmd_option = 'option' in inspect.getargspec(self.__cmd.execute)[0]

    def __load_config(self, options_common):
        self.__config_user = load_config_user(options_common)

    def __load_shell(self, shell_name):
        shell_object = None
        if self.__cmd_output_shell:
            try:
                return Shell(shell_name)
            except Exception as e:
                raise CmdError('Can not load shell: {0}'.format(e))
        return shell_object
