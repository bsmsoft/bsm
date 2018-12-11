import sys
import json

from bsm.loader import load_common


class Shell(object):
    def __init__(self, shell_name, cmd_name, app_root):
        self.__shell = load_common(shell_name, 'bsm.shell')(cmd_name, app_root)

        self.__script = ''

    def clear_script(self):
        self.__script = ''

    def newline(self, line_number=1):
        self.__script += '\n'*line_number

    def add_env(self, env):
        if 'unset_env' in env:
            for e in env['unset_env']:
                self.__script += self.__shell.unset_env(e)
        if 'set_env' in env:
            for k, v in env['set_env'].items():
                self.__script += self.__shell.set_env(k, v)
        if 'unalias' in env:
            for a in env['unalias']:
                self.__script += self.__shell.unalias(a)
        if 'alias' in env:
            for k, v in env['alias'].items():
                self.__script += self.__shell.alias(k, v)

    def add_script(self, script_type, *args, **kargs):
        method_name = 'script_' + script_type
        self.__script += getattr(self.__shell, method_name)(*args, **kargs)

    def __getattr__(self, name):
        def method(*args, **kargs):
            self.__script += getattr(self.__shell, name)(*args, **kargs)
        return method

    @property
    def script(self):
        return self.__script


def _generate_script(output, shell, cmd_name):
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
            shell.init_script(cmd_name)
        elif script_type == 'exit':
            shell.exit_script(cmd_name)

def main(shell_name='sh', cmd_name='bsm'):
    output = sys.stdin.read()

    shell = Shell(shell_name)

    _generate_script(output, shell, cmd_name)

    sys.stdout.write(shell.script)
