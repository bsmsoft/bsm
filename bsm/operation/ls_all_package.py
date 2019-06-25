from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LsAllPackage(Base):
    def execute(self):
        packages = {}

        cur_pkgs = self._env.current_packages()

        for category in self._config['package_runtime']:
            for subdir in self._config['package_runtime'][category]:
                for package in self._config['package_runtime'][category][subdir]:
                    for version in self._config['package_runtime'][category][subdir][package]:
                        active = (package in cur_pkgs and category == cur_pkgs[package]['category'] and \
                                subdir == cur_pkgs[package]['subdir'] and version == cur_pkgs[package]['version'])
                        packages.setdefault(package, [])
                        packages[package].append({'category': category, 'subdir': subdir, 'version': version, 'active': active})

        return packages
