import sys
import inspect

from cepcenv.error import CepcenvError


class LoadError(CepcenvError):
    pass

class ModuleNotFoundError(LoadError):
    pass

class ClassNotFoundError(LoadError):
    pass

class NotAClassError(LoadError):
    pass


def load_module(module_name):
    try:
        __import__(module_name)
    except ImportError as e:
        raise ModuleNotFoundError('Module "%s" not found' % module_name)
    return sys.modules[module_name]


def load_class(module_name, class_name):
    m = load_module(module_name)

    try:
        c = getattr(m, class_name)
    except AttributeError as e:
        raise ClassNotFoundError('Class "%s" not found in module "%s"' % (class_name, module_name))

    if not inspect.isclass(c):
        raise NotAClassError('"%s" in module "%s" is not a class' % (class_name, module_name))

    return c
