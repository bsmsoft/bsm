from bsm.loader import load_common


class OutputError(Exception):
    pass


class Output(object):
    def __init__(self, fmt):
        if not fmt:
            fmt = 'direct'
        try:
            self.__output = load_common(fmt, 'bsm.cmd.output')()
        except Exception as e:
            raise OutputError('Can not load output "{0}": {1}'.format(fmt, e))

    def dump(self, value):
        return self.__output.dump(value)
