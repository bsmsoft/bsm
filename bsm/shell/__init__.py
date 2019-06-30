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

    def setup_script(self):
        return self.__shell.setup_script()

    @property
    def script(self):
        return self.__script
