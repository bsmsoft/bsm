import os
import shutil

def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_to_camel(name):
    return name.title().replace('_', '')


def safe_rmdir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)

def safe_mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def safe_copy(src, dst):
    if not os.path.exists(dst):
        directory = os.path.dirname(dst)
        safe_mkdir(directory)
    shutil.copy2(src, dst)


def expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))


def ensure_list(item):
    return item if isinstance(item, list) else [item]

def unique_list(seq):
    unique = []
    for item in seq:
        if item not in unique:
            unique.append(item)
    return unique
