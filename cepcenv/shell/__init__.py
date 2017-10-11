from cepcenv.loader import load_common


def load_shell(shell_name):
    return load_common(shell_name, 'cepcenv.shell')


class Shell(object):
    def comment(self, content):
        lines = content.rstrip().split('\n')
        newlines = map(lambda x:'# '+x, lines)
        return '\n'.join(newlines) + '\n'

    def echo(self, content):
        lines = content.rstrip().split('\n')

        # "\" should be escaped
        # "'" will be converted into four chars "'\''"
        newlines = map(lambda x:'echo \'' + x.replace('\\', '\\\\').replace('\'', '\'\\\'\'') + '\'', lines)

        return '\n'.join(newlines) + '\n'
