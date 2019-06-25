from bsm.cmd import CmdError
from bsm.cmd.pkg_base import PkgBase

class PkgLs(PkgBase):
    def execute(self, list_all, package):
        self._check_release()

        if list_all:
            packages = self._bsm.ls_all_package()
        else:
            packages = self._bsm.ls_active_package()

        if package:
            if package not in packages:
                raise CmdError('Package "{0}" is not found'.format(package))
            return self.__output_result({package: packages[package]})

        return self.__output_result(packages)

    def __output_result(self, packages):
        if self._output_format != 'plain':
            return packages

        max_package_length = 1
        max_category_length = 1
        max_subdir_length = 1
        max_version_length = 1

        for pkg, cfgs in packages.items():
            for cfg in cfgs:
                package_length = len(pkg)
                if max_package_length < package_length:
                    max_package_length = package_length

                category_length = len(cfg['category'])
                if max_category_length < category_length:
                    max_category_length = category_length

                subdir_length = len(cfg['subdir'])
                if max_subdir_length < subdir_length:
                    max_subdir_length = subdir_length

                version_length = len(str(cfg['version']))
                if max_version_length < version_length:
                    max_version_length = version_length

        result_lines = []
        for pkg, cfgs in packages.items():
            for cfg in cfgs:
                line = '| {0:{pkg_width}} | {1:{ctg_width}} | {2:{sd_width}} | {3:{ver_width}} |'\
                        .format(pkg, cfg['category'], cfg['subdir'], cfg['version'], \
                        pkg_width=max_package_length, ctg_width=max_category_length, sd_width=max_subdir_length, ver_width=max_version_length)
                if cfg.get('active'):
                    line = '* ' + line
                else:
                    line = '  ' + line
                result_lines.append(line)

        return result_lines
