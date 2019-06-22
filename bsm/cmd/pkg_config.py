from bsm.cmd.pkg_base import PkgBase

class PkgConfig(PkgBase):
    def execute(self, category, subdir, version, package):
        self._check_release()

        category, subdir, package, version = self._process_param(package, category, subdir, version)

        pkg_cfg = self._bsm.package_config(package, category, subdir, version)

        return pkg_cfg['config']
