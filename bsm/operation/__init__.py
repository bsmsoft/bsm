from bsm.error import OperationNotFoundError

from bsm.loader import load_common


class Base(object):
    def __init__(self, prop, env):
        self._prop = prop
        self._env = env


class Operation(object):
    def __init__(self, prop, env):
        self.__prop = prop
        self.__env = env

    def execute(self, op_name, *args, **kargs):
        try:
            operation = load_common(op_name, 'bsm.operation')(self.__prop, self.__env)
        except Exception as e:
            raise OperationNotFoundError('Can not load operation "{0}": {1}'.format(op_name, e))

        return operation.execute(*args, **kargs)
