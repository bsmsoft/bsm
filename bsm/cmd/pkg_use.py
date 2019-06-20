from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgUse(PkgBase):
    def execute(self, detect_category, category, subdir, version, package):
        self._check_release()

        if detect_category and category is None:
            category = self._current_category()

        ctg, sd, ver = self._bsm.load_package(package, category, subdir, version)
        _logger.info('Load package "{0}" successfully'.format(package))

        pkg_path = self._bsm.package_path(package, ctg, sd, ver)

        result = {}
        result['category'] = ctg
        result['subdir'] = sd
        result['name'] = package
        result['version'] = ver
        result['main_dir'] = pkg_path['main_dir']
        return result
