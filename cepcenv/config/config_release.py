import os
import tempfile

from cepcenv.git import list_remote_tag
from cepcenv.git import Git

from cepcenv.config import load_config
from cepcenv.config import ConfigError

from cepcenv.util import safe_cpdir
from cepcenv.util import safe_rmdir


class ConfigReleaseError(Exception):
    pass


class ConfigRelease(object):
    def __init__(self, config_version):
        self.__config_version = config_version

        self.__load_config()

    def __load_config(self):
        self.__config_release = {}

        config_dir = os.path.join(self.__config_version.def_dir, 'config')
        if not os.path.exists(config_dir):
            raise ConfigReleaseError('Release definition directory "{0}" not found'.format(config_dir))

        for k in ['version', 'main', 'package', 'attribute', 'install']:
            config_file = os.path.join(config_dir, k+'.yml')
            try:
                self.__config_release[k] = load_config(config_file)
            except ConfigError as e:
                raise ConfigReleaseError('Fail to load config file "{0}": {1}'.format(config_file, e))

        for k, v in self.__config_release['main']['category']['categories'].items():
            if 'root' in v:
                v['root'] = v['root'].format(**self.__config_version.config)


    def get(self, key, default_value=None):
        return self.__config_release.get(key, default_value)

    def package_root(self, pkg):
        pkg_root = ''

        pkg_cfg = self.__config_release['package'][pkg]

        categories = self.__config_release['main']['category']['categories']
        if pkg_cfg['category'] in categories and 'root' in categories[pkg_cfg['category']]:
            path = pkg_cfg.get('path')
            if not path:
                path = ''
            pkg_root = os.path.join(categories[pkg_cfg['category']]['root'], path, pkg)

        return pkg_root

    @property
    def config(self):
        return self.__config_release
