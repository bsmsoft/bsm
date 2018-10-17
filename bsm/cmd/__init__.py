import sys
import traceback

import click

from bsm import BSM
from bsm.loader import load_common
from bsm.config.release import ConfigReleaseError

from bsm.cmd.output import Output

from bsm.logger import get_logger
_logger = get_logger()


class CmdError(Exception):
    pass


class CmdResult(object):
    def __init__(self, output='', script_type='unknown'):
        self.__output = output
        self.__script_type = script_type

    @property
    def output(self):
        return self.__output

    @property
    def script_type(self):
        return self.__script_type


class Cmd(object):
    def execute(self, cmd_name, obj, *args, **kwargs):
        bsm = BSM(obj['config_entry'])

        try:
            cmd = load_common(cmd_name, 'bsm.cmd')(bsm, obj['output']['format'] is None)
        except Exception as e:
            raise CmdError('Can not load command "{0}": {1}'.format(cmd_name, e))

        try:
            cmd_result = cmd.execute(*args, **kwargs)

            if isinstance(cmd_result, CmdResult):
                result_output = cmd_result.output
                if obj['output']['shell']:
                    result_script_type = cmd_result.script_type
            else:
                result_output = cmd_result

            if obj['output']['env']:
                result_output = {'value': result_output, 'env': bsm.env().env_all()}

            output = Output(obj['output']['format'])
            final_output = output.dump(result_output)

            if obj['output']['shell']:
                output_shell = Output('json')
                final_output = output_shell.dump({'output': final_output, 'script_type': result_script_type, 'env': bsm.env().env_change()})
        except ConfigReleaseError as e:
            _logger.error(str(e))
            _logger.critical('Can not load release version: {0}'.format(cmd_kwargs.get('version_name')))
            sys.exit(2)
        except Exception as e:
            _logger.critical('Fatal error ({0}): {1}'.format(type(e).__name__, e))
            if bsm.config('output')['verbose']:
                _logger.critical('\n{0}'.format(traceback.format_exc()))
            sys.exit(1)

        click.echo(final_output)
