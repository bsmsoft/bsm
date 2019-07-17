import sys
import inspect

from bsm.util import snake_to_camel

from bsm.error import LoadError
from bsm.error import LoadModuleError
from bsm.error import AttributeNotFoundError
from bsm.error import FunctionNotFoundError
from bsm.error import NotCallableError
from bsm.error import ClassNotFoundError
from bsm.error import NotAClassError

def load_module(module_name):
    try:
        __import__(module_name)
    except ImportError as e:
        raise LoadModuleError('Load module "{0}" error: {1}'.format(module_name, e))
    return sys.modules[module_name]


def load_func(module_name, func_name):
    mod = load_module(module_name)

    try:
        f = getattr(mod, func_name)
    except AttributeError as e:
        raise FunctionNotFoundError(
            'Function "{0}" not found in module "{1}": {2}'.format(func_name, module_name, e))

    if not callable(f):
        raise NotCallableError(
            '"{0}" in module "{1}" is not callable'.format(func_name, module_name))

    return f

def load_class(module_name, class_name):
    mod = load_module(module_name)

    try:
        cls = getattr(mod, class_name)
    except AttributeError as e:
        raise ClassNotFoundError(
            'Class "{0}" not found in module "{1}": {2}'.format(class_name, module_name, e))

    if not inspect.isclass(cls):
        raise NotAClassError('"{0}" in module "{1}" is not a class'.format(class_name, module_name))

    return cls

def load_common(name, module_prefix):
    name_underscore = name.replace('-', '_')
    module_name = '{0}.{1}'.format(module_prefix, name_underscore)
    class_name = snake_to_camel(name_underscore)

    try:
        cls = load_class(module_name, class_name)
    except LoadError as e:
        raise LoadError('Load "{0}:{1}" error: {2}'.format(module_prefix, name, e))

    return cls

def load_relative(module_cur, module_rel, attr_name):
    parent_module_seq = module_cur.split('.')[:-1]
    full_module_name = '.'.join(parent_module_seq + [module_rel])

    mod = load_module(full_module_name)

    try:
        cls = getattr(mod, attr_name)
    except AttributeError as e:
        raise AttributeNotFoundError(
            'Attribute "{0}" not found in module "{1}": {2}'.format(attr_name, module_rel, e))

    return cls
