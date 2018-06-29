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


_logger = get_logger()


class CmdError(Exception):
    pass


class Cmd(object):
    def execute(self, cmd_name, obj, *args, **kwargs):
        config_entry = obj['config_entry'].copy()
        if 'output_format' not in config_entry:
            config_entry['output_format'] = 'command'
        bsm = BSM(config_entry)

        try:
            self.__cmd = load_common(cmd_name, 'bsm.cmd')(bsm)
        except Exception as e:
            raise CmdError('Can not load command "{0}": {1}'.format(cmd_name, e))

        try:
            result = self.__cmd.execute(**cmd_kwargs)
            if obj['output_for_shell']:
                final_output = {'output': result, 'env': bsm.
            click.echo(result)
        except ConfigReleaseError as e:
            _logger.error(str(e))
            _logger.critical('Can not load release version: {0}'.format(cmd_kwargs.get('version_name')))
            sys.exit(2)
        except Exception as e:
            _logger.critical('Fatal error ({0}): {1}'.format(type(e).__name__, e))
            if self.__config_user['verbose']:
                _logger.critical('\n{0}'.format(traceback.format_exc()))
            sys.exit(1)
