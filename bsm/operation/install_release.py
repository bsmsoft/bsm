import os

from bsm.git import Git

from bsm.util import safe_cpdir
from bsm.util import safe_rmdir

from bsm.operation import Base
from bsm.operation.util import list_versions


class ReleaseVersionError(Exception):
    pass


def _install_from_dir(src_dir, dst_dir):
    safe_rmdir(dst_dir)
    safe_cpdir(src_dir, dst_dir)


def _install_from_git_repo(src_repo, release_version, version_pattern, dst_dir, git_temp):
    git = Git(dst_dir, git_temp=git_temp)

    versions = list_versions(src_repo, version_pattern, git)

    if release_version not in versions:
        raise ReleaseVersionError('Release version "{0}" does not exist in repo {1}'.format(release_version, src_repo))

    release_tag = versions[release_version]

    safe_rmdir(dst_dir)

    git.clone(src_repo)
    git.checkout(release_tag)
    git.clear_git_info()


class InstallRelease(Base):
    def execute(self):
        if 'version' not in self._config['scenario']:
            raise ReleaseVersionError('No release version specified')

        self.__install_definition()
        self.__install_handler()

        self._config.reset()

        return self._config['scenario']['version']

    def __install_definition(self):
        conf = self._config['scenario']
        content_dir = self._config['release_path']['content_dir']
        version_pattern = self._config['app']['version_pattern']
        git_temp = self._config['app'].get('git_temp')

        if 'release_source' in conf and conf['release_source']:
            _install_from_dir(conf['release_source'], content_dir)
        elif 'version' in conf and conf['version']:
            _install_from_git_repo(conf['release_repo'], conf['version'], version_pattern, content_dir, git_temp)
        else:
            _logger.warn('No release specified, nothing to do')

    def __install_handler(self):
        conf = self._config['release_path']
        handler_dir = conf['handler_dir']
        handler_module_dir = conf['handler_module_dir']

        safe_cpdir(handler_dir, handler_module_dir)

        handler_init = os.path.join(handler_module_dir, '__init__.py')
        if not os.path.exists(handler_init):
            open(handler_init, 'w').close()
