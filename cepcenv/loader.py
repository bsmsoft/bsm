import sys
import inspect

from cepcenv.util import snake_to_camel


class LoadError(Exception):
    pass

class LoadModuleError(LoadError):
    pass

class AttributeNotFoundError(LoadError):
    pass

class FunctionNotFoundError(AttributeNotFoundError):
    pass

class NotCallableError(LoadError):
    pass

class ClassNotFoundError(AttributeNotFoundError):
    pass

class NotAClassError(LoadError):
    pass


def load_module(module_name):
    try:
        __import__(module_name)
    except ImportError as e:
        raise LoadModuleError('Load module "{0}" error: {1}'.format(module_name, e))
    return sys.modules[module_name]


def load_func(module_name, func_name):
    m = load_module(module_name)

    try:
        f = getattr(m, func_name)
    except AttributeError as e:
        raise FunctionNotFoundError('Function "{0}" not found in module "{1}": {2}'.format(func_name, module_name, e))

    if not callable(f):
        raise NotCallableError('"{0}" in module "{1}" is not callable'.format(func_name, module_name))

    return f

def load_class(module_name, class_name):
    m = load_module(module_name)

    try:
        c = getattr(m, class_name)
    except AttributeError as e:
        raise ClassNotFoundError('Class "{0}" not found in module "{1}": {2}'.format(class_name, module_name, e))

    if not inspect.isclass(c):
        raise NotAClassError('"{0}" in module "{1}" is not a class'.format(class_name, module_name))

    return c

def load_common(name, module_prefix):
    name_underscore = name.replace('-', '_')
    module_name = '{0}.{1}'.format(module_prefix, name_underscore)
    class_name = snake_to_camel(name_underscore)

    try:
        c = load_class(module_name, class_name)
    except LoadError as e:
        raise LoadError('Load "{0}:{1}" error: {2}'.format(module_prefix, name, e))

    return c

def load_relative(module_name, attr_name):
    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    caller_module_name = caller_module.__name__
    parent_module_seq = caller_module_name.split('.')[:-1]
    full_module_name = '.'.join(parent_module_seq + [module_name])

    m = load_module(full_module_name)

    try:
        c = getattr(m, attr_name)
    except AttributeError as e:
        raise AttributeNotFoundError('Attribute "{0}" not found in module "{1}": {2}'.format(attr_name, module_name, e))

    return c
