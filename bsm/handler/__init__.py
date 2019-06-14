import sys

from bsm.loader import load_func
from bsm.loader import LoadError

from bsm.const import HANDLER_MODULE_NAME

from bsm.logger import get_logger
_logger = get_logger()


class HandlerNotFoundError(Exception):
    pass

class HandlerNotAvailableError(Exception):
    pass


class Handler(object):
    def __init__(self, extra_python_path=None):
        self.__extra_python_path = extra_python_path
        if extra_python_path is not None:
            _logger.debug('Prepend python path: {0}'.format(extra_python_path))
            sys.path.insert(0, extra_python_path)

        self.__module_list = [HANDLER_MODULE_NAME, 'bsm.handler']

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not self.__extra_python_path:
            return
        _logger.debug('Clear python path: {0}'.format(self.__extra_python_path))
        sys.path.remove(self.__extra_python_path)
        self.__extra_python_path = None

    def run(self, handler_name, *args, **kwargs):
        for m in self.__module_list:
            try:
                f = load_func(m+'.'+handler_name, 'run')
            except LoadError as e:
                _logger.debug('Not able to load handler "{0}:{1}"'.format(m, handler_name))
                continue

            try:
                result = f(*args, **kwargs)
                _logger.debug('Run handler "{0}:{1}"'.format(m, handler_name))
                return result
            except HandlerNotAvailableError as e:
                _logger.debug('Handler not available for "{0}:{1}"'.format(m, handler_name))
                continue

        raise HandlerNotFoundError('Could not find handler for "{0}"'.format(handler_name))
