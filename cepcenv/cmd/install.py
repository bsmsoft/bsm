from cepcenv.manager import Manager

class Install(object):
    def execute(self, config, version_config, release_config):
        manager = Manager(config, version_config, release_config)
        manager.install()
