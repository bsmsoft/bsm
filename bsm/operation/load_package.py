from bsm.config.util import find_package

from bsm.handler import Handler

from bsm.operation import Base


class LoadPackageError(Exception):
    pass


class LoadPackage(Base):
    def execute(self, package, category=None, subdir=None, version=None):
        category_priority = self._config['category']['priority']

        with Handler(self._config['release_path']['handler_python_dir']) as h:
            ctg, sd, ver = find_package(h, category_priority, self._config['package_runtime'], package, category, subdir, version)

        if ctg is None:
            raise LoadPackageError('Specified package "{0}" not found for category "{1}", subdir "{2}", version "{3}"'.format(package, category, subdir, version))

        pkg_cfg = self._config['package_runtime'].package_config(ctg, sd, package, ver)['config']

        self._env.unload_package(package)
        self._env.load_package(pkg_cfg)

        return ctg, sd, ver
