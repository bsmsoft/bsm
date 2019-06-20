from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LsActivePackage(Base):
    def execute(self):
        packages = {}

        for package, value in self._env.current_packages().items():
            packages.setdefault(package, [])
            packages[package].append({'category': value['category'], 'subdir': value['subdir'], 'version': value['version'], 'active': True})

        return packages
