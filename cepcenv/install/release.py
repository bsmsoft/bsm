import os

from cepcenv.util import safe_cpdir
from cepcenv.util import safe_rmdir


class ReleaseVersionNotExistError(Exception):
    pass


def __install_from_dir(src_dir, dst_dir):
    safe_cpdir(src_dir, dst_dir)


def __install_from_git_repo(src_repo, release_version, dst_dir):
    release_tag = 'v'+release_version
    if release_tag not in list_remote_tag(src_repo):
        raise ReleaseVersionNotExistError('Release version "{0}" does not exist in repo {1}'.format(release_version, src_repo))

    git = Git(dst_dir)
    git.clone(src_repo)
    git.checkout(release_tag)

    safe_rmdir(os.path.join(dst_dir, '.git'))


def install_definition(config_version):
    cv = config_version.config
    def_dir = config_version.def_dir

    if 'softdef_dir' in cv and cv['softdef_dir']:
        __install_from_dir(cv['softdef_dir'], def_dir)
    elif 'version' in cv and cv['version']:
        __install_from_git_repo(cv['softdef_repo'], cv['version'], def_dir)

def install_handler(config_version):
    def_dir = config_version.def_dir
    handler_module_dir = config_version.handler_module_dir

    safe_cpdir(os.path.join(def_dir, 'handler'), handler_module_dir)

    handler_init = os.path.join(handler_module_dir, '__init__.py')
    if not os.path.exists(handler_init):
        open(handler_init, 'w').close()
