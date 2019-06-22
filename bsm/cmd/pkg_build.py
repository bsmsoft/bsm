from bsm.cmd import CmdResult
from bsm.cmd.pkg_base import PkgBase

class PkgBuild(PkgBase):
    def execute(self, category, subdir, version, rebuild, package):
        self._check_release()

        category, subdir, package, version = self._process_param(package, category, subdir, version)

        commands = self._bsm.build_package(package, category, subdir, version, rebuild)

        return CmdResult(commands=commands)
