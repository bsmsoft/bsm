from bsm.cmd.pkg_base import PkgBase

class PkgPath(PkgBase):
    def execute(self, detect_category, category, subdir, version, list_all, package):
        self._check_release()

        if detect_category and category is None:
            category = self._current_category()

        pkg_path = self._bsm.package_path(package, category, subdir, version)

        if not list_all:
            return pkg_path['main_dir']

        return pkg_path
