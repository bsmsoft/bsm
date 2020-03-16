import sys
import subprocess
import traceback

import click

from bsm import BSM
from bsm.error import BSMError
from bsm.loader import load_common
from bsm.shell import Shell
from bsm.cmd.output import Output
from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class CmdError(Exception):
    pass


class CmdResult(object):
    def __init__(self, output='', commands=None, script_types=None):
        self.__output = output

        self.__commands = ensure_list(commands) if commands else []
        self.__script_types = ensure_list(script_types) if script_types else []

    @property
    def output(self):
        return self.__output

    @property
    def commands(self):
        return self.__commands

    @property
    def script_types(self):
        return self.__script_types


def _convert_cmd_result(result):
    if isinstance(result, CmdResult):
        return result
    return CmdResult(output=result)


def _generate_script(cmd_name, app_root, shell_name, output, commands, env_changes, script_types):
    try:
        shell = Shell(shell_name, cmd_name, app_root)
    except Exception as e:
        raise CmdError('Can not load shell "{0}": {1}'.format(shell_name, e))

    shell.comment('Setup env and alias')
    shell.add_env(env_changes)

    shell.newline()
    shell.comment('Add definition script')
    for script_type in script_types:
        shell.add_script(script_type)

    shell.newline()
    shell.comment('Run commands')
    for command in commands:
        cmd = command.get('cmd', [])
        cwd = command.get('cwd', None)
        if cmd:
            shell.echo('='*80)
            shell.echo('= Start to run: {0}'.format(cmd))
            if cwd is not None:
                shell.echo('= Cwd: {0}'.format(cwd))
            shell.run(cmd, cwd)
            shell.echo('- End command')
            shell.echo('-'*80)

    shell.newline()
    shell.comment('Final output')
    if output:
        shell.echo(output)

    shell.newline()
    shell.comment('Shell script finished')

    return shell.script

def _run_commands(commands):
    for run_cmd in commands:
        cmd = run_cmd.get('cmd', [])
        cwd = run_cmd.get('cwd', None)
        if cmd:
            _logger.debug('Running command: %s', cmd)
            _logger.debug('Command cwd: %s', cwd)
            subprocess.call(cmd, cwd=run_cmd.get('cwd', None))


class Base(object):
    def __init__(self, bsm, output_format):
        self._bsm = bsm
        self._output_format = output_format


class Cmd(object):
    @staticmethod
    def execute(subcmd_name, obj, *args, **kwargs):
        if 'check_cli' in obj and obj['check_cli']:
            click.echo('BSM:COMMAND_LINE_INTERFACE_OK')
            return

        bsm = BSM(obj['prop_entry'])

        output_format = obj['output']['format']

        try:
            command = load_common(subcmd_name, 'bsm.cmd')(bsm, output_format)
        except Exception as e:
            raise CmdError('Can not load command "{0}": {1}'.format(subcmd_name, e))

        try:
            cmd_result = _convert_cmd_result(command.execute(*args, **kwargs))

            result_output = cmd_result.output

            env_final = bsm.env_final()
            env_changes = bsm.apply_env_changes()

            if obj['output']['env']:
                result_output = {
                    'output': result_output,
                    'env_final': env_final,
                    'env_changes': env_changes,
                }

            output = Output(output_format)
            final_output = output.dump(result_output)

            if obj['output']['shell']:
                final_output = _generate_script(
                    bsm.prop('app')['cmd_name'], bsm.prop('app').get('app_root', ''),
                    obj['output']['shell'], final_output,
                    cmd_result.commands, env_changes, cmd_result.script_types)

            if final_output:
                new_line = not final_output.endswith('\n')
                click.echo(final_output, nl=new_line)

            if not obj['output']['shell']:
                _run_commands(cmd_result.commands)
        except BSMError as e:
            _logger.critical('Fatal error (%s): %s', type(e).__name__, e)
            if bsm.prop('output')['verbose']:
                _logger.critical('\n%s', traceback.format_exc())
            sys.exit(2)
