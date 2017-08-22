class Install(object):
    def execute(self, config, scenario_name, release_root, release_config_file):
        scenario_config_cmd = {}
        if release_root:
            scenario_config_cmd['release_root'] = release_root
        if release_config_file:
            scenario_config_cmd['release_config'] = release_config_file

        scenario = Scenario(config, scenario_name, scenario_config_cmd)

        manager = Manager(config)
        manager.install(scenario)
