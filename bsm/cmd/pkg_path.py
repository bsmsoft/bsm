from bsm.cmd.pkg_base import PkgBase

class PkgPath(PkgBase):
    def execute(self, category, subdir, version, list_all, package):
        self._check_release()

        if package is None:
            category, subdir, package, version = self._current_package()

        pkg_path = self._bsm.package_path(package, category, subdir, version)

        if not list_all:
            return pkg_path['main_dir']

        return pkg_path
