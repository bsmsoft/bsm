import os

from cepcenv.config import load_config
from cepcenv.config import dump_config

from cepcenv.logger import get_logger
_logger = get_logger()

class PackageNotFoundError(Exception):
    pass

class PackageManager(object):
    def __init__(self, config_version, config_release):
        self.__config_version = config_version
        self.__config_release = config_release

        self.__load_categories()
        self.__load_packages()
        self.__load_package_dir_list()

    def __load_categories(self):
        self.__categories = {}
        for ctg, cfg in self.__config_release.config['setting']['category']['categories'].items():
            required_config = cfg.get('required_config', [])
            required_config_not_found = False
            for i in required_config:
                if i not in self.__config_version.config:
                    required_config_not_found = True
                    break
            if required_config_not_found:
                continue

            self.__categories[ctg] = {}
            self.__categories[ctg]['pre_check'] = cfg.get('pre_check', False)
            self.__categories[ctg]['install'] = cfg.get('install', False)
            self.__categories[ctg]['auto_env'] = cfg.get('auto_env', False)
            self.__categories[ctg]['auto_package'] = cfg.get('auto_package', False)
            self.__categories[ctg]['root'] = cfg.get('root')

            if 'root' in cfg:
                self.__categories[ctg]['root'] = cfg['root'].format(**self.__config_version.config)
            else:
                self.__categories[ctg]['install'] = False
                self.__categories[ctg]['auto_package'] = False

    def __load_packages(self):
        self.__pkgs = {}
        for pkg in self.__config_release.get('package', {}):
            pkg_info = {}
            pkg_info['name'] = pkg
            pkg_info['package'] = self.__config_release.get('package')[pkg]
            pkg_info['attribute'] = self.__config_release.get('attribute', {}).get(pkg, {})
            pkg_info['install'] = self.__config_release.get('install', {}).get(pkg, {})
            pkg_info['check'] = self.__config_release.get('check', {}).get(pkg, {})

            category = pkg_info['package'].get('category')
            pkg_info['category'] = self.__categories.get(category, {})
            pkg_info['dir'] = self.__package_dir(pkg, pkg_info)
            self.__pkgs[pkg] = pkg_info

    def __load_package_dir_list(self):
        self.__pkg_dir_list = {}
        install_path_name = self.__config_release.get('setting', {}).get('path_usage', {}).get('install', {})
        for pkg, pkg_info in self.__pkgs.items():
            if not pkg_info['category'].get('auto_env'):
                continue

            for k, v in pkg_info['attribute'].get('path', {}).items():
                if k not in install_path_name:
                    continue
                path_key = install_path_name[k].format(package=pkg)
                self.__pkg_dir_list[path_key] = v.format(**pkg_info['dir'])

    def __package_root(self, pkg_info):
        category_root = pkg_info['category']['root']
        path = pkg_info['package'].get('path', '')
        pkg_name = pkg_info['name']
        return os.path.join(category_root, path, pkg_name)

    def __package_dir(self, pkg, pkg_info):
        pkg_dir = {}
        if pkg_info['category'] and pkg_info['category'].get('install'):
            package_root = self.__package_root(pkg_info)
            version = pkg_info['package'].get('version', 'unknown')
            location = self.__config_release.config['attribute'][pkg]['location']

            pkg_dir['root'] = package_root

            package_work_root = os.path.join(package_root, '.cepcenv', version)
            pkg_dir['status'] = os.path.join(package_work_root, 'status')
            pkg_dir['log'] = os.path.join(package_work_root, 'log')
            pkg_dir['download'] = os.path.join(package_work_root, 'download')

            pkg_dir['source'] = os.path.join(package_root, version, location['source']).rstrip(os.sep)
            pkg_dir['build'] = os.path.join(package_root, version, location['build']).rstrip(os.sep)
            pkg_dir['install'] = os.path.join(package_root, version, location['install']).rstrip(os.sep)

        return pkg_dir


    def __install_status_file(self, pkg):
        return os.path.join(self.__pkgs[pkg]['dir']['status'], 'install.yml')

    def __load_install_status(self, pkg, action):
        try:
            install_status = load_config(self.__install_status_file(pkg))
            if not isinstance(install_status, dict):
                return {}
            return install_status
        except:
            return {}

    def is_ready(self, pkg, action):
        if not self.__pkgs[pkg]['category'].get('install'):
            return False

        install_status = self.__load_install_status(pkg, action)
        return action in install_status and \
                'finished' in install_status[action] and \
                install_status[action]['finished']

    def save_action_status(self, pkg, action, start, end):
        if pkg not in self.__pkgs:
            raise PackageNotFoundError('Package {0} not found'.format(pkg))
        if not self.__pkgs[pkg]['category'].get('install'):
            _logger.warn('Will not save status for: {0}.{1}'.format(pkg, action))
            return

        install_status = self.__load_install_status(pkg, action)

        if action not in install_status:
            install_status[action] = {}
        install_status[action]['finished'] = True
        install_status[action]['start'] = start
        install_status[action]['end'] = end

        dump_config(install_status, self.__install_status_file(pkg))


    def package_all(self):
        return self.__pkgs

    def package_info(self, pkg):
        return self.__pkgs[pkg]

    def package_dir_list(self):
        return self.__pkg_dir_list
