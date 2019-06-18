import os

from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class PkgInstall(Base):
    def execute(self, category, subdir, version, category_origin, subdir_origin, version_origin, package):
        if category is None:
            ctg, sd = self._bsm.detect_category(os.getcwd())
            if ctg:
                category = ctg

        final_category, final_subdir, final_version = self._bsm.install_package(package, category, subdir, version, category_origin, subdir_origin, version_origin)

        _logger.info('Package "{0}" installed successfully'.format(package))

        result = {}
        result['category'] = final_category
        result['subdir'] = final_subdir
        result['version'] = final_version
        result['main_dir'] = self._bsm.config('package_runtime')[final_category][final_subdir][package][final_version]['package_path']['main_dir']

        return result
