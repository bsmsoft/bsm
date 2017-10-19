from cepcenv.install import Install as CepcenvInstall

class Install(object):
    def execute(self, config, config_version):
        obj = CepcenvInstall(config, config_version)
        obj.run()
