import os
import subprocess

from cepcenv.util import safe_rmdir


class GitError(Exception):
    pass

class GitNotFoundError(GitError):
    pass


def _git_cmd(cwd, cmd, *args):
    full_cmd = ['git', cmd] + list(args)
    try:
        p = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        out, err = p.communicate()
        out = out.decode()
        err = err.decode()
        ret = p.returncode
    except OSError as e:
        raise GitNotFoundError('Can not run git command "{0}": {1}'.format(cmd, e))
    except Exception as e:
        raise GitError('Exception while running git command "{0}": {1}'.format(cmd, e))

    if ret != 0:
        raise GitError('Git command "{0}" failed with exit code {1}: {2}'.format(' '.join(full_cmd), ret, err))

    return out


def _list_remote(remote_path, ref):
    ref_arg = '--' + ref
    out = _git_cmd(None, 'ls-remote', '--refs', ref_arg, remote_path)
    items = []
    for i in out.splitlines():
        i = i.strip().split()[1]
        i = i[len(ref)+6:]
        if i:
            items.append(i)
    return items

def list_remote_branch(remote_path):
    return _list_remote(remote_path, 'heads')

def list_remote_tag(remote_path):
    return _list_remote(remote_path, 'tags')


class Git(object):
    def __init__(self, repo_path):
        self.__repo_path = repo_path

    def clone(self, remote_path):
        out = _git_cmd(None, 'clone', remote_path, self.__repo_path)

    def checkout(self, branch):
        out = _git_cmd(self.__repo_path, 'checkout', branch)

    def clear_git_info(self):
        safe_rmdir(os.path.join(self.__repo_path, '.git'))


    def __list_ref(self, ref):
        ref_prefix = 'refs/' + ref
        out = _git_cmd(self.__repo_path, 'for-each-ref', '--format=%(refname)', ref_prefix)
        items = []
        for i in out.splitlines():
            i = i.strip()
            i = i[len(ref_prefix)+1:]
            if i:
                items.append(i)
        return items

    def list_branch(self):
        return self.__list_ref('heads')

    def list_tag(self):
        return self.__list_ref('tags')
