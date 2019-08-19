import os
import subprocess

from bsm.util import safe_rmdir
from bsm.util import expand_path

from bsm.error import GitError
from bsm.error import GitNotFoundError
from bsm.error import GitUnknownCommandError
from bsm.error import GitEmptyUrlError

from bsm.logger import get_logger
_logger = get_logger()


COMMAND_MAP = {
    'clone': [None, 'clone', '{url}', '{path}'],
    'checkout': ['{path}', 'checkout', '{branch}'],
    'ls-remote-branches': [None, 'ls-remote', '--refs', '--heads', '{url}'],
    'ls-remote-tags': [None, 'ls-remote', '--refs', '--tags', '{url}'],
    'ls-branches': ['{path}', 'for-each-ref', '--format=%(refname:short)', 'refs/heads'],
    'ls-tags': ['{path}', 'for-each-ref', '--format=%(refname:short)', 'refs/tags'],
}


def _git_cmd(cwd, exe, *args):
    full_cmd = [exe] + list(args)
    _logger.debug('Run git command: %s', full_cmd)

    try:
        p = subprocess.Popen(full_cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd)
        out, err = p.communicate()
        ret = p.returncode
    except Exception as e:
        raise GitError(
            'Exception while running git command "{0}": {1}'.format(full_cmd, e))

    if ret != 0:
        raise GitError(
            'Git command "{0}" failed with exit code {1}: {2}'.format(' '.join(full_cmd), ret, err))

    return out.decode()


def _find_git(git_temp=None):
    try:
        _git_cmd(None, 'git', 'version')
        _logger.debug('Use system git')
        return 'git'
    except GitError as e:
        pass

    if git_temp is not None:
        try:
            _git_cmd(None, expand_path(git_temp), 'version')
            _logger.debug('Use temporary git from %s', git_temp)
            return git_temp
        except GitError as e:
            pass

    _logger.error('Git command not found')
    raise GitNotFoundError('Can not find git command')


def _parse_ref_list(out):
    return [i.strip() for i in out.splitlines()]


def _parse_remote_list(out):
    refs = []
    for line in out.splitlines():
        name = line.strip().split()[1]
        name_short = name.split('/')[2]
        refs.append(name_short)
    return refs


class Git(object):
    def __init__(self, path=None, git_temp=None):
        self.__path = path
        self.__git_exec = _find_git(git_temp)

    def __run_cmd(self, command, **kwargs):
        if command not in COMMAND_MAP:
            _logger.error('Do not known how to run: %s', command)
            raise GitUnknownCommandError(
                'Do not known how to run: {0}'.format(command))

        params = kwargs.copy()
        if self.__path is not None:
            params['path'] = self.__path

        cwd = COMMAND_MAP[command][0]
        if cwd is not None:
            cwd = cwd.format(**params)
        git_args = [v.format(**params) for v in COMMAND_MAP[command][1:]]
        return _git_cmd(cwd, self.__git_exec, *git_args)

    def clone(self, url):
        self.__run_cmd('clone', url=url)

    def checkout(self, branch):
        self.__run_cmd('checkout', branch=branch)

    def clear_git_info(self):
        if self.__path is not None:
            safe_rmdir(os.path.join(self.__path, '.git'))

    def ls_branches(self):
        out = self.__run_cmd('ls-branches')
        return _parse_ref_list(out)

    def ls_tags(self):
        out = self.__run_cmd('ls-tags')
        return _parse_ref_list(out)

    def __ls_remote(self, url, ls_type):
        if not url:
            raise GitEmptyUrlError('Git url not specified')
        out = self.__run_cmd('ls-remote-'+ls_type, url=url)
        return _parse_remote_list(out)

    def ls_remote_branches(self, url):
        return self.__ls_remote(url, 'branches')

    def ls_remote_tags(self, url):
        return self.__ls_remote(url, 'tags')
