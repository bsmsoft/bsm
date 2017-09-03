import os
import tempfile
import subprocess

from cepcenv.git import Git

from cepcenv.config import load_config
from cepcenv.config import ConfigError

from cepcenv.util import expand_path
from cepcenv.util import safe_rmdir


class ReleaseVersionNotExistError(Exception):
    pass

class ReleaseVersionMismatchError(Exception):
    pass


class Release(object):
    def __init__(self, version_config):
        if 'release_info' in version_config and version_config['release_info']:
            self.__load_from_info(version_config['release_info'])
        elif 'release_version' in version_config and version_config['release_version']:
            self.__load_from_repo(version_config['release_repo'], version_config['release_version'])
        else:
            raise ReleaseError('Not enough release information')

        self.__validate_release_version(version_config)


    def __load_from_info(self, release_info):
        self.__release_config = self.__load_release_from_dir(expand_path(release_info))

    def __load_from_repo(self, release_repo, release_version):
        try:
            repo_dir = tempfile.mkdtemp(prefix='cepcsoft_tmp_')
            git = Git(repo_dir)
            git.clone(release_repo)
            release_tag = 'v'+release_version
            if release_tag not in git.list_tag():
                raise ReleaseVersionNotExistError('Release version "{0}" does not exist in repo {1}'.format(release_version, release_repo))
            git.checkout(release_tag)

            self.__release_config = self.__load_release_from_dir(repo_dir)
        finally:
            safe_rmdir(repo_dir)

        return {}

    def __load_release_from_dir(self, dir_name):
        release_config = {}

        try:
            release_config['release_version'] = load_config(os.path.join(dir_name, 'release_version.yml'))
        except ConfigError as e:
            pass

        try:
            release_config['package'] = load_config(os.path.join(dir_name, 'package.yml'))
        except ConfigError as e:
            print(e)
            pass

        return release_config


    def __validate_release_version(self, version_config):
        if 'release_version' in version_config:
            version_in_version = version_config['release_version']

            if 'release_version' in self.__release_config:
                version_in_release = release_config['release_version']

                if version_in_version != version_in_release:
                    raise ReleaseVersionMismatchError('Release version "{0}" and "{1}" do not match'.format(version_in_version, version_in_release))
            else:
                self.__release_config['release_version'] = version_in_version

    def __str__(self):
        return str(self.__release_config)

    @property
    def config(self):
        return self.__release_config
