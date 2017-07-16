from cepcenv.cmd.cmdcommon import CmdCommon

class Install(CmdCommon):
    def execute(self, config, version):
        get_scenario()
        download_release_info()
        parse_release_info()
        build_dag()

        download_packages()
        compile_packages()
