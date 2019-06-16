from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LsAllPackage(Base):
    def execute(self):
        packages = []

        for category in self._config['package_runtime']:
            for subdir in self._config['package_runtime'][category]:
                for package in self._config['package_runtime'][category][subdir]:
                    for version, value in self._config['package_runtime'][category][subdir][package].items():
                        packages.append((package, category, subdir, version))

        return packages
