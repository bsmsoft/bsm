import os
import subprocess

from cepcenv.util import safe_rmdir

from cepcenv.logger import get_logger
_logger = get_logger()


class GitError(Exception):
    pass

class GitNotFoundError(GitError):
    pass

class GitUnknownCommandError(GitError):
    pass


COMMAND_MAP = {
    'git': {
        'clone': [None, 'clone', '{url}', '{path}'],
        'checkout': ['{path}', 'checkout', '{branch}'],
        'ls-remote-branches': [None, 'ls-remote', '--refs', '--heads', '{url}'],
        'ls-remote-tags': [None, 'ls-remote', '--refs', '--tags', '{url}'],
        'ls-branches': ['{path}', 'for-each-ref', '--format=%(refname:short)', 'refs/heads'],
        'ls-tags': ['{path}', 'for-each-ref', '--format=%(refname:short)', 'refs/tags'],
    },
    'gittemp': {
        'clone': [None, 'clone', '{url}', '{path}'],
        'checkout': [None, 'checkout', '{path}', '{branch}'],
        'ls-remote-branches': [None, 'ls-remote', 'branches', '{url}'],
        'ls-remote-tags': [None, 'ls-remote', 'tags', '{url}'],
        'ls-branches': [None, 'ls', 'branches', '{path}'],
        'ls-tags': [None, 'ls', 'tags', '{path}'],
    },
}


def _git_cmd(cwd, exe, *args):
    full_cmd = [exe] + list(args)
    try:
        p = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        out, err = p.communicate()
#        out = out.decode()
#        err = err.decode()
        ret = p.returncode
    except Exception as e:
        raise GitError('Exception while running git command "{0}": {1}'.format(full_cmd, e))

    if ret != 0:
        raise GitError('Git command "{0}" failed with exit code {1}: {2}'.format(' '.join(full_cmd), ret, err))

    return out

def _find_git():
    try:
        _git_cmd(None, 'git', 'version')
        _logger.debug('Use system git')
        return 'git', 'git'
    except Exception as e:
        pass

    if '_CEPCENV_GITTEMP' in os.environ:
        gittemp_exec = os.environ['_CEPCENV_GITTEMP']
        try:
            _git_cmd(None, gittemp_exec, 'version')
            _logger.debug('Use temporary git from {0}'.format(gittemp_exec))
            return 'gittemp', gittemp_exec
        except Exception as e:
            pass

    _logger.error('Git command not found')
    raise GitNotFoundError('Can not find git command')


class Git(object):
    def __init__(self, path=None):
        self.__path = path
        self.__git_type, self.__git_exec = _find_git()

    def __run_cmd(self, command, **kwargs):
        if command not in COMMAND_MAP[self.__git_type]:
            _logger.error('Do not known how to run: {0}'.format(command))
            raise GitUnknownCommandError('Do not known how to run: {0}'.format(command))

        params = kwargs.copy()
        if self.__path is not None:
            params['path'] = self.__path

        cwd = COMMAND_MAP[self.__git_type][command][0]
        if cwd is not None:
            cwd = cwd.format(**params)
        git_args = [v.format(**params) for v in COMMAND_MAP[self.__git_type][command][1:]]
        return _git_cmd(cwd, self.__git_exec, *git_args)

    def clone(self, url):
        out = self.__run_cmd('clone', url=url)

    def checkout(self, branch):
        out = self.__run_cmd('checkout', branch=branch)

    def clear_git_info(self):
        if self.__path is not None:
            safe_rmdir(os.path.join(self.__path, '.git'))


    def __parse_ref_list(self, out):
        return [i.strip() for i in out.splitlines()]

    def ls_branches(self):
        out = self.__run_cmd('ls-branches')
        return self.__parse_ref_list(out)

    def ls_tags(self):
        out = self.__run_cmd('ls-tags')
        return self.__parse_ref_list(out)


    def __parse_remote_list(self, out):
        refs = []
        for line in out.splitlines():
            name = line.strip().split()[1]
            name_short = line.split('/')[2]
            refs.append(name_short)
        return refs

    def ls_remote_branches(self, url):
        out = self.__run_cmd('ls-remote-branches', url=url)
        return self.__parse_remote_list(out)

    def ls_remote_tags(self, url):
        out = self.__run_cmd('ls-remote-tags', url=url)
        return self.__parse_remote_list(out)
