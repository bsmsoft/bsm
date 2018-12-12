from bsm.loader import load_common


class Base(object):
    def __init__(self, config, env):
        self._config = config
        self._env = env


class OperationError(Exception):
    pass


class Operation(object):
    def __init__(self, config, env):
        self.__config = config
        self.__env = env

    def execute(self, op_name, *args, **kargs):
        try:
            op = load_common(op_name, 'bsm.operation')(self.__config, self.__env)
        except Exception as e:
            raise OperationError('Can not load operation "{0}": {1}'.format(op_name, e))

        return op.execute(*args, **kargs)
