from bsm.operation import Base

class LoadReleasePackages(Base):
    def execute(self):
        self._env.unload_packages()

        category_priority = self._config['category']['priority']
        category_auto_env = [ctg for ctg in category_priority if self._config['category']['content'].get(ctg, {}).get('auto_env')]

        for category in reversed(category_auto_env):
            if category not in self._config['package_runtime']:
                continue
            for subdir in self._config['package_runtime'][category]:
                for package in self._config['package_runtime'][category][subdir]:
                    for version, value in self._config['package_runtime'][category][subdir][package].items():
                        self._env.load_package(value['config'])
