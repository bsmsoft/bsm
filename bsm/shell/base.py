class Base(object):
    def __init__(self, cmd_name, app_root):
        self._cmd_name = cmd_name
        self._app_root = app_root

    def comment(self, content):
        lines = content.rstrip().split('\n')
        newlines = map(lambda x:'# '+x, lines)
        return '\n'.join(newlines) + '\n'

    def run(self, command):
        args = ['\''+arg+'\'' for arg in command]
        return ' '.join(args) + '\n'
