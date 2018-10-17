import sys
import json

from bsm.loader import load_common


class Shell(object):
    def __init__(self, shell_name):
        self.__shell = load_common(shell_name, 'bsm.shell')()

        self.__script = ''

    def clear_script(self):
        self.__script = ''

    def newline(self, line_number=1):
        self.__script += '\n'*line_number

    def __getattr__(self, name):
        def method(*args, **kargs):
            self.__script += getattr(self.__shell, name)(*args, **kargs)
        return method

    @property
    def script(self):
        return self.__script


def _generate_script(output, shell, command):
    try:
        result = json.loads(output)
    except Exception as e:
        shell.echo(output)
        return

    if not isinstance(result, dict):
        shell.echo(output)
        return

    if 'output' in result:
        shell.echo(result['output'])

    if 'env' in result:
        shell.set_env(result['env']['set_env'])
        shell.unset_env(result['env']['unset_env'])

    if 'script_type' in result:
        script_type = result['script_type']
        if script_type == 'init':
            shell.init_script(command)
        elif script_type == 'exit':
            shell.exit_script(command)

def main(shell_name='sh', command='bsm'):
    output = sys.stdin.read()

    shell = Shell(shell_name)

    _generate_script(output, shell, command)

    sys.stdout.write(shell.script)
