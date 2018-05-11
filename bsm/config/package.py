import os

from bsm.config.common import Common

from bsm.util.config import load_config
from bsm.util.config import dump_config

from bsm.util import safe_mkdir

from bsm.logger import get_logger
_logger = get_logger()

class ConfigPackageError(Exception):
    pass

class Package(Common):
    def load_package(self, config_app, config_release, config_category):
        self.__package_work_dir = config_app['package_work_dir']

        self.__load_packages(config_release, config_category)
        self.__load_package_dir_list()

    def __load_packages(self, config_release, config_category):
        for pkg, pkg_config in config_release.get('package', {}).items():
            category = pkg_config.get('category')
            if category not in config_category:
                _logger.error('Category "{0}" does not exist for package "{1}"'.format(category, pkg))
                continue

            pkg_info = {'name': pkg}

            pkg_info['config_category'] = config_category[category]

            pkg_info['config'] = pkg_config
            pkg_info['dir'] = self.__package_dir(pkg_info)

            self[pkg] = pkg_info

    def __load_package_dir_list(self):
        self.__pkg_dir_list = {}
        install_path_name = self.__config_release.get('setting', {}).get('path_usage', {}).get('install', {})
        for pkg, pkg_info in self.items():
            if not pkg_info.get('config_category', {}).get('auto_env'):
                continue

            for k, v in pkg_info.get('config', {}).get('path', {}).items():
                if k not in install_path_name:
                    continue
                path_key = install_path_name[k].format(package=pkg)
                self.__pkg_dir_list[path_key] = v.format(**pkg_info['dir'])


    def __package_dir(self, pkg_info):
        def _package_root(pkg_info):
            category_root = pkg_info.get('config_category', {})['root']
            subdir = pkg_info.get('config', {}).get('subdir', '')
            return os.path.join(category_root, subdir, pkg_info['name'])

        pkg_dir = {}
        config_category = pkg_info.get('config_category', {})
        if config_category.get('install'):
            pkg_config = pkg_info.get('config', {})
            version = pkg_config.get('version', 'unknown_version')
            location = pkg_config.get('location', {})

            package_root = _package_root(pkg_info)
            pkg_dir['root'] = package_root

            package_work_root = os.path.join(package_root, self.__package_work_dir, version)
            pkg_dir['status'] = os.path.join(package_work_root, 'status')
            pkg_dir['log'] = os.path.join(package_work_root, 'log')
            pkg_dir['download'] = os.path.join(package_work_root, 'download')

            pkg_dir['source'] = os.path.join(package_root, version, location['source']).rstrip(os.sep)
            pkg_dir['build'] = os.path.join(package_root, version, location['build']).rstrip(os.sep)
            pkg_dir['install'] = os.path.join(package_root, version, location['install']).rstrip(os.sep)

        return pkg_dir


    def __install_status_file(self, pkg):
        return os.path.join(self[pkg]['dir']['status'], 'install.yml')

    def __release_status_file(self, pkg):
        return os.path.join(self[pkg]['dir']['status'], 'release.yml')

    def __load_status(self, status_file):
        try:
            install_status = load_config(status_file)
            if not isinstance(install_status, dict):
                return {}
            return install_status
        except:
            return {}

    def is_finished(self, pkg, action):
        if not self[pkg]['config_category'].get('install'):
            return False

        install_status = self.__load_status(self.__install_status_file(pkg))
        return 'steps' in install_status and \
                action in install_status['steps'] and \
                'finished' in install_status['steps'][action] and \
                install_status['steps'][action]['finished']

    def save_action_status(self, pkg, action, start, end):
        if pkg not in self:
            raise ConfigPackageError('Package {0} not found'.format(pkg))
        if not self[pkg]['config_category'].get('install'):
            _logger.warn('Will not save install status for: {0}.{1}'.format(pkg, action))
            return

        install_status = self.__load_status(self.__install_status_file(pkg))

        if 'steps' not in install_status:
            install_status['steps'] = {}
        if action not in install_status['steps']:
            install_status['steps'][action] = {}
        install_status['steps'][action]['finished'] = True
        install_status['steps'][action]['start'] = start
        install_status['steps'][action]['end'] = end

        safe_mkdir(self[pkg]['dir']['status'])
        dump_config(install_status, self.__install_status_file(pkg))

    def save_release_status(self, pkg, end_time):
        if pkg not in self:
            raise ConfigPackageError('Package {0} not found'.format(pkg))
        if not self[pkg]['config_category'].get('install'):
            _logger.warn('Will not save release status for: {0}'.format(pkg))
            return

        release_status = self.__load_status(self.__release_status_file(pkg))

        if 'version' not in release_status:
            release_status['version'] = []
        release_version = self.__config_release.get('version')
        if release_version and release_version not in release_status['version']:
            release_status['version'].append(release_version)

        safe_mkdir(self[pkg]['dir']['status'])
        dump_config(release_status, self.__release_status_file(pkg))


#    def package_all(self):
#        return self.__pkgs

    def package_info(self, pkg):
        return self.get(pkg, {})

    @property
    def package_dir_list(self):
        return self.__pkg_dir_list
