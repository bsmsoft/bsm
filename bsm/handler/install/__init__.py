from bsm.loader import load_relative

from bsm.error import LoadError
from bsm.error import HandlerNotAvailableError

def run(param):
    try:
        run_func = load_relative(__name__, 'install.'+param['action'], 'run')
    except LoadError:
        raise HandlerNotAvailableError

    if not callable(run_func):
        raise HandlerNotAvailableError

    return run_func(param)
