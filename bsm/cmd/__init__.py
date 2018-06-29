import sys
import traceback

import click

from bsm import BSM
from bsm.loader import load_common
from bsm.output import Output
from bsm.config.release import ConfigReleaseError

from bsm.logger import get_logger
_logger = get_logger()


class CmdError(Exception):
    pass


class Cmd(object):
    def execute(self, cmd_name, obj, *args, **kwargs):
        bsm = BSM(obj['config_entry'])

        try:
            self.__cmd = load_common(cmd_name, 'bsm.cmd')(bsm, obj['output']['format'] is None)
        except Exception as e:
            raise CmdError('Can not load command "{0}": {1}'.format(cmd_name, e))

        try:
            cmd_result = self.__cmd.execute(*args, **kwargs)

            if obj['output']['env']:
                output_result = {'value': cmd_result, 'env': bsm.env().env_all()}
            else:
                output_result = cmd_result
            output = Output(obj['output']['format'])
            final_output = output.dump(output_result)

            if obj['output']['shell']:
                output_shell = Output('json')
                final_output = output_shell.dump({'output': final_output, 'env': bsm.env().env_change()})
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
