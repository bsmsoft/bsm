class Install(object):
    def execute(self, config, release_root, release_config_file, scenario_name):
        scenario_config = {}

        if scenario_name:
            scenario_config = Scenario(config).load(scenario_name)

        if release_root:
            scenario_config['release_root'] = release_root

        if release_config_file:
            scenario_config['release_config'] = release_config_file

        manager = Manager(config, scenario_config)
        

#        get_scenario()
#        download_release_info()
#        parse_release_info()
#        build_dag()
#
#        download_packages()
#        compile_packages()
