class Base(object):
    def __init__(self, cmd_name, app_root):
        self._cmd_name = cmd_name
        self._app_root = app_root

    def run(self, command, cwd=None):
        args = ['\''+str(arg)+'\'' for arg in command]
        run_line = ' '.join(args) + '\n'
        if not cwd:
            return run_line

        cd_line = 'cd \'' + cwd + '\'\n'
        cd_old_line = 'cd -\n'
        return cd_line + run_line + cd_old_line
