import os
import tempfile

from cepcenv.git import Git

from cepcenv.config.util import load_config
from cepcenv.config.util import ConfigError

from cepcenv.util import expand_path
from cepcenv.util import safe_cpdir
from cepcenv.util import safe_rmdir


class ReleaseError(Exception):
    pass

class ReleaseVersionNotExistError(ReleaseError):
    pass

class ReleaseVersionMismatchError(ReleaseError):
    pass


def __load_from_info(release_info):
    return __load_release_from_dir(expand_path(release_info))

def __load_from_repo(release_repo, release_version):
    repo_dir = tempfile.mkdtemp(prefix='cepcsoft_tmp_')

    try:
        git = Git(repo_dir)
        git.clone(release_repo)
        release_tag = 'v'+release_version
        if release_tag not in git.list_tag():
            raise ReleaseVersionNotExistError('Release version "{0}" does not exist in repo {1}'.format(release_version, release_repo))
        git.checkout(release_tag)

        return __load_release_from_dir(repo_dir)
    finally:
        safe_rmdir(repo_dir)

def __load_release_from_dir(dir_name):
    release_config = {}

    for k in ['version', 'package', 'install']:
        try:
            release_config[k] = load_config(os.path.join(dir_name, k+'.yml'))
        except ConfigError as e:
            print(e)
            pass

    return release_config


def load_release_config(version_config):
    if 'release_info' in version_config and version_config['release_info']:
        return __load_from_info(version_config['release_info'])
    elif 'version' in version_config and version_config['version']:
        return __load_from_repo(version_config['release_repo'], version_config['version'])

    return {}



def __copy_from_info(release_info, dst_dir):
    return __copy_release_handler_from_dir(expand_path(release_info), dst_dir)

def __copy_from_repo(release_repo, release_version, dst_dir):
    repo_dir = tempfile.mkdtemp(prefix='cepcsoft_tmp_')

    try:
        git = Git(repo_dir)
        git.clone(release_repo)
        release_tag = 'v'+release_version
        if release_tag not in git.list_tag():
            raise ReleaseVersionNotExistError('Release version "{0}" does not exist in repo {1}'.format(release_version, release_repo))
        git.checkout(release_tag)

        return __copy_release_handler_from_dir(repo_dir, dst_dir)
    finally:
        safe_rmdir(repo_dir)

def __copy_release_handler_from_dir(dir_name, dst_dir):
    safe_cpdir(os.path.join(dir_name, 'handler'), os.path.join(dst_dir, 'handler', 'cepcenv_handler_run_avoid_conflict'))
    with open(os.path.join(dst_dir, 'handler', 'cepcenv_handler_run_avoid_conflict', '__init__.py'), 'w'):
        pass


def copy_release_handler(version_config, dst_dir):
    if 'release_info' in version_config and version_config['release_info']:
        __copy_from_info(version_config['release_info'], dst_dir)
    elif 'version' in version_config and version_config['version']:
        __copy_from_repo(version_config['release_repo'], version_config['version'], dst_dir)
