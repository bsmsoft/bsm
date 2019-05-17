from bsm.loader import load_relative
from bsm.loader import LoadError

def avail(action, param):
    try:
        run_func = load_relative('install.'+action, 'run')
    except LoadError as e:
        return False

    if not callable(run_func):
        return False

    return True

def run(action, param):
    run_func = load_relative('install.'+action, 'run')

    return run_func(param)
