import os
import re
import shutil
import subprocess

def camel_to_snake(name, delim='_'):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1%s\2'%delim, name)
    return re.sub('([a-z0-9])([A-Z])', r'\1%s\2'%delim, s1).lower()

def snake_to_camel(name, delim='_'):
    return name.title().replace(delim, '')


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
    temp_path = os.path.expanduser(path)
    temp_path = os.path.expandvars(temp_path)
    return os.path.normpath(temp_path)


def ensure_list(item):
    return item if isinstance(item, list) else [item]

def unique_list(seq):
    unique = []
    for item in seq:
        if item not in unique:
            unique.append(item)
    return unique


def call(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    return p.communicate()[0].decode()
