from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LoadReleasePackages(Base):
    def execute(self):
        self._env.unload_packages()

        category_priority = self._config['release'].get('setting', {}).get('category_priority', [])
        category_auto_env = [ctg for ctg in category_priority if self._config['category'].get(ctg, {}).get('auto_env')]
        category_auto_env += [ctg for ctg, cfg in self._config['category'].items() if ctg not in category_auto_env and cfg.get('auto_env')]

        for category in category_auto_env:
            if category not in self._config['package_runtime']:
                continue
            for subdir in self._config['package_runtime'][category]:
                for package in self._config['package_runtime'][category][subdir]:
                    for version, value in self._config['package_runtime'][category][subdir][package].items():
                        self._env.load_package(value['config'])
