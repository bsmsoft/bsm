from bsm.config.util import find_package
from bsm.config.util import package_path

from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.handler import Handler

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class MatchInstallPackage(Base):
    def execute(self, package, category=None, subdir=None, version=None, category_origin=None, subdir_origin=None, version_origin=None):
        category_priority = self._config['category_priority']

        from_install = False

        with Handler(self._config['release_path']['handler_python_dir']) as h:
            ctg, sd, ver = find_package(h, category_priority, self._config['package_runtime'], package, category, subdir, version)

            if ctg is not None:
                _logger.debug('Package destination found: {0}.{1}.{2}.{3}'.format(ctg, sd, package, ver))
                return ctg, sd, ver, None, None, None, False

            ctg_org, sd_org, ver_org = find_package(h, category_priority, self._config['package_runtime'], package, category_origin, subdir_origin, version_origin)
            if ctg_org is None:
                _logger.debug('Try to find reference in config_package_install')
                ctg_org, sd_org, ver_org = find_package(h, category_priority, self._config['package_install'], package, category_origin, subdir_origin, version_origin)
                if ctg_org is None:
                    _logger.error('Could not find matching reference package to install "{0}"'.format(package))
                    return None, None, None, None, None, None, False
                from_install = True
                _logger.debug('Package reference found in config_package_install: {0}.{1}.{2}.{3}'.format(ctg_org, sd_org, package, ver_org))
            else:
                _logger.debug('Package reference found in config_package_runtime: {0}.{1}.{2}.{3}'.format(ctg_org, sd_org, package, ver_org))

            if category is None:
                category = ctg_org
            if subdir is None:
                subdir = sd_org
            if version is None:
                version = ver_org

        return category, subdir, version, ctg_org, sd_org, ver_org, from_install
