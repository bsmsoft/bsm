from cepcenv.install import Install as CepcenvInstall

class Install(object):
    def execute(self, config, config_version, source):
        transformer = source + '_source'

        obj = CepcenvInstall(config, config_version, [transformer])
        obj.run()
