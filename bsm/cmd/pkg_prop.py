from bsm.cmd.pkg_base import PkgBase

class PkgProp(PkgBase):
    def execute(self, category, subdir, version, package):
        self._check_release()

        category, subdir, package, version = self._process_param(package, category, subdir, version)

        pkg_props = self._bsm.package_props(package, category, subdir, version)

        return pkg_props['prop']
