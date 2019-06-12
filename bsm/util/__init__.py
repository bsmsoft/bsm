import os
import sys
import re
import shutil
import subprocess
import datetime
import pprint


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

def walk_rel_dir(directory, rel_dir=''):
    if not os.path.isdir(directory):
        raise StopIteration
    res = os.listdir(directory)
    for r in res:
        full_path = os.path.join(directory, r)
        if os.path.isfile(full_path):
            yield (full_path, rel_dir, r)
            continue
        if os.path.isdir(full_path):
            new_rel_dir = os.path.join(rel_dir, r)
            for next_full_path, next_rel_dir, next_f in walk_rel_dir(full_path, new_rel_dir):
                yield (next_full_path, next_rel_dir, next_f)


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

def call_and_log(cmd, log, cwd=None, env=None, input=None):
    log.write('='*80 + '\n')
    log.write(' - Start time: {0}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    log.write(' - Command: {0}\n'.format(cmd))
    log.write(' - Cwd: {0}\n'.format(cwd))
    log.write(' - Env:\n{0}\n'.format(pprint.pformat(env)))
    log.write('-'*80 + '\n')
    log.flush()

    try:
        ret, out, err = call(cmd, stdout=log, cwd=cwd, env=env, input=input)
    except OSError as e:
        log.write('OSError: {0}\n'.format(e))
        log.write('Command not found: {0}\n'.format(cmd[0]))
        ret = 127

    log.flush()

    return ret


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
