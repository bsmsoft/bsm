import os


CEPCENV_HOME = os.path.dirname(os.path.realpath(__file__))


class CepcEnvError(Exception):
    pass


def version():
    with open(os.path.join(CEPCENV_HOME, 'VERSION'), 'r') as f:
        ver = f.read()
    return ver.strip()


class CepcEnv(object):
    def __init__(self):
        pass

    def help(self, args):
        pass

    def execute(self, args):
        if not args:
            print('need args')
            return 1

        command = args[0]
        print('Command:', command)
        print('Args:', args[1:])

        return 0
