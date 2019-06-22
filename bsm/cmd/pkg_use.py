from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgUse(PkgBase):
    def execute(self, category, subdir, version, package):
        self._check_release()

        category, subdir, package, version = self._process_param(package, category, subdir, version)

        self._bsm.load_package(package, category, subdir, version)
        _logger.info('Load package "{0}" successfully'.format(package))

        pkg_path = self._bsm.package_path(package, category, subdir, version)

        result = {}
        result['category'] = category
        result['subdir'] = subdir
        result['name'] = package
        result['version'] = version
        result['main_dir'] = pkg_path['main_dir']
        return result
