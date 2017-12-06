import os
import sys
import re
import shutil
import subprocess


def camel_to_snake(name, delim='_'):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1{0}\2'.format(delim), name)
    return re.sub('([a-z0-9])([A-Z])', r'\1{0}\2'.format(delim), s1).lower()

def snake_to_camel(name, delim='_'):
    return name.title().replace(delim, '')


def is_str(var):
    if sys.version_info[0] >= 3:
        return isinstance(var, str)
    return isinstance(var, basestring)


def ensure_list(item):
    return item if isinstance(item, list) else [item]

def unique_list(seq):
    unique = []
    for item in seq:
        if item not in unique:
            unique.append(item)
    return unique


def safe_rmdir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)

def safe_mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def safe_copy(src, dst):
    directory = os.path.dirname(dst)
    safe_mkdir(directory)
    shutil.copy2(src, dst)

def safe_cpdir(src, dst):
    directory = os.path.dirname(dst)
    safe_mkdir(directory)
    safe_rmdir(dst)
    shutil.copytree(src, dst)

def safe_mvdir(src, dst):
    directory = os.path.dirname(dst)
    safe_mkdir(directory)
    safe_rmdir(dst)
    shutil.move(src, dst)


def expand_path(path):
    temp_path = os.path.expanduser(path)
    temp_path = os.path.expandvars(temp_path)
    temp_path = os.path.abspath(temp_path)
    return os.path.normpath(temp_path)


def check_output(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    return p.communicate()[0].decode()

def call(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=None, env=None, input=None):
    p = subprocess.Popen(args,
            stdout=stdout, stderr=stderr, stdin=subprocess.PIPE,
            cwd=cwd, env=env)
    out, err = p.communicate(input=input)
    ret = p.returncode
    return (ret, out, err)


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
