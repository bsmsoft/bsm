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
    def load(self, pkg, pkg_config, pkg_category, pkg_work_dir):
        self.__pkg_work_dir = pkg_work_dir

        self['name'] = pkg

        self['category'] = pkg_category
        self['config'] = pkg_config

        self['version'] = self['config'].get('version', 'unknown_version')

        self.__load_package_dir()


    def __load_package_dir(self):
        self['dir'] = {}
        self['dir']['location'] = {}

        if 'root' not in self['category'] or self['category']['root'] is None:
            return

        category_root = self['category']['root']
        subdir = self['config'].get('subdir', '')
        package_root = os.path.join(category_root, subdir, self['name'])
        content_root = os.path.join(package_root, self['version'])
        work_root = os.path.join(package_root, self.__pkg_work_dir, self['version'])
        status_root = os.path.join(work_root, 'status')
        log_root = os.path.join(work_root, 'log')

        self['dir']['root'] = package_root
        self['dir']['content'] = content_root
        self['dir']['work'] = work_root
        self['dir']['status'] = status_root
        self['dir']['log'] = log_root

        for k, v in self['config'].get('location', {}).items():
            self['dir']['location'][k] = v.format(package_content=content_root, package_work=work_root)


    def __install_status_file(self):
        return os.path.join(self['dir']['status'], 'install.yml')

    def __release_status_file(self):
        return os.path.join(self['dir']['status'], 'release.yml')

    def __load_status(self, status_file):
        try:
            install_status = load_config(status_file)
            if not isinstance(install_status, dict):
                return {}
            return install_status
        except:
            return {}

    def is_finished(self, action):
        if not self['category'].get('install'):
            return False

        install_status = self.__load_status(self.__install_status_file())
        return 'steps' in install_status and \
                action in install_status['steps'] and \
                'finished' in install_status['steps'][action] and \
                install_status['steps'][action]['finished']

    def save_action_status(self, action, start, end):
        if not self['category'].get('install'):
            _logger.warn('Will not save install status for: {0}.{1}'.format(self['name'], action))
            return

        install_status = self.__load_status(self.__install_status_file())

        if 'steps' not in install_status:
            install_status['steps'] = {}
        if action not in install_status['steps']:
            install_status['steps'][action] = {}
        install_status['steps'][action]['finished'] = True
        install_status['steps'][action]['start'] = start
        install_status['steps'][action]['end'] = end

        safe_mkdir(self['dir']['status'])
        dump_config(install_status, self.__install_status_file())

    def save_release_status(self, end_time):
        if not self['category'].get('install'):
            _logger.warn('Will not save release status for: {0}'.format(self['name']))
            return

        release_status = self.__load_status(self.__release_status_file())

        if 'version' not in release_status:
            release_status['version'] = []
        release_version = self.__config_release.get('version')
        if release_version and release_version not in release_status['version']:
            release_status['version'].append(release_version)

        safe_mkdir(self['dir']['status'])
        dump_config(release_status, self.__release_status_file())
