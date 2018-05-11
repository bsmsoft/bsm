from bsm.loader import load_common


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

        return {'value': op.execute(*args, **kargs), 'env': self.__env.xxx()}
