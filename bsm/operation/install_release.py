import os

from bsm.git import Git

from bsm.util import safe_cpdir
from bsm.util import safe_rmdir

from bsm.operation.base import Base


class ReleaseVersionNotExistError(Exception):
    pass


def _install_from_dir(src_dir, dst_dir):
    safe_rmdir(dst_dir)
    safe_cpdir(src_dir, dst_dir)


def _install_from_git_repo(src_repo, release_version, dst_dir):
    git = Git(dst_dir)

    release_tag = 'v'+release_version
    if release_tag not in git.ls_remote_tags(src_repo):
        raise ReleaseVersionNotExistError('Release version "{0}" does not exist in repo {1}'.format(release_version, src_repo))

    safe_rmdir(dst_dir)

    git.clone(src_repo)
    git.checkout(release_tag)
    git.clear_git_info()


class InstallRelease(Base):
    def execute(self):
        self.__install_definition()
        self.__install_handler()

    def __install_definition(self):
        conf = self._config['scenario']
        def_dir = conf.version_path['def_dir']

        if 'release_source' in conf and conf['release_source']:
            _install_from_dir(conf['release_source'], def_dir)
        elif 'version' in conf and conf['version']:
            _install_from_git_repo(conf['release_repo'], conf['version'], def_dir)

    def __install_handler(self):
        version_path = self._config['scenario'].version_path
        def_dir = version_path['def_dir']
        handler_dir = version_path['handler_dir']
        handler_module_dir = version_path['handler_module_dir']

        safe_cpdir(handler_dir, handler_module_dir)

        handler_init = []
        handler_init.append(os.path.join(handler_module_dir, '__init__.py'))
        for d in os.listdir(handler_module_dir):
            if os.path.isdir(os.path.join(handler_module_dir, d)):
                handler_init.append(os.path.join(handler_module_dir, d, '__init__.py'))

        for f in handler_init:
            if not os.path.exists(f):
                open(f, 'w').close()
