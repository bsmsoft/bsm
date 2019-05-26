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
        if extra_python_dir is not None:
            sys.path.insert(0, extra_python_dir)

        self.__module_list = [HANDLER_MODULE_NAME, 'bsm.handler']

    def __del__(self):
        self.clear_python_path()

    def clear_python_path(self):
        if not self.__extra_python_path:
            return
        sys.path.remove(self.__extra_python_dir)
        self.__extra_python_dir = None

    def run(handler_name, *args, **kwargs):
        for m in self.__module_list:
            try:
                f = load_func(m+'.'+handler_name, 'run')
            except Exception as e:
                _logger.debug('Failed to load handler {0} / {1}'.format(m, handler_name))
                continue

            try:
                result = f(*args, **kwargs)
                _logger.debug('Run handler {0} / {1}'.format(m, handler_name))
                return result
            except HandlerNotAvailableError as e:
                _logger.debug('Handler not available for {0} / {1}'.format(m, handler_name))
                continue
            except Exception as e:
                raise

        raise HandlerNotFoundError('Could not find handler for "{0}"'.format(handler_name))
