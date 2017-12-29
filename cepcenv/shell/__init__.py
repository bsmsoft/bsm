from cepcenv.loader import load_common


class Shell(object):
    def __init__(self, shell_name):
        self.__shell = load_common(shell_name, 'cepcenv.shell')()

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
