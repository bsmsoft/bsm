from bsm.prop.util import find_package

from bsm.handler import Handler

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class MatchInstallPackage(Base):
    def execute(self, package, category=None, subdir=None, version=None,
                category_origin=None, subdir_origin=None, version_origin=None):
        category_priority = self._prop['category_priority']

        from_install = False

        with Handler(self._prop['release_path']['handler_python_dir']) as h:
            ctg, subd, ver = find_package(
                h, category_priority, self._prop['packages_runtime'],
                package, category, subdir, version)

            if ctg is not None:
                _logger.debug('Package destination found: %s.%s.%s.%s', ctg, subd, package, ver)
                return ctg, subd, ver, None, None, None, False

            ctg_org, subd_org, ver_org = find_package(
                h, category_priority, self._prop['packages_runtime'],
                package, category_origin, subdir_origin, version_origin)

            if ctg_org is None:
                _logger.debug('Try to find reference in prop_packages_install')
                ctg_org, subd_org, ver_org = find_package(
                    h, category_priority, self._prop['packages_install'],
                    package, category_origin, subdir_origin, version_origin)

                if ctg_org is None:
                    _logger.error('Could not find matching reference package to install "%s"',
                                  package)
                    return None, None, None, None, None, None, False
                from_install = True
                _logger.debug(
                    'Package reference found in prop_packages_install: %s.%s.%s.%s',
                    ctg_org, subd_org, package, ver_org)
            else:
                _logger.debug(
                    'Package reference found in prop_packages_runtime: %s.%s.%s.%s',
                    ctg_org, subd_org, package, ver_org)

            if category is None:
                category = ctg_org
            if subdir is None:
                subdir = subd_org
            if version is None:
                version = ver_org

        return category, subdir, version, ctg_org, subd_org, ver_org, from_install
