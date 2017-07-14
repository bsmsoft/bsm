from cepcenv.loader import load_class
from cepcenv.loader import LoadError

from cepcenv.util import snake_to_camel


class ShellError(Exception):
    pass


def load_shell(shell_name):
    module_name = 'cepcenv.shell.' + shell_name
    class_name = snake_to_camel(shell_name)

    try:
        c = load_class(module_name, class_name)
    except LoadError as e:
        raise ShellError('Load shell "%s" error: %s' % (shell_name, e))

    return c


class Shell(object):
    def comment(self, content):
        lines = content.split('\n')
        newlines = map(lambda x:'# '+x, lines)
        return '\n'.join(newlines)
