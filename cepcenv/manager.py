class Manager(object):
    def __init__(self, config):
        self.__config = config
        self.__platform = SoftwarePlatform(self.__config).all()

    def install(self, scenario_name):
        self.__scenario = Scenario(self.__config).load(scenario_name)

        get_scenario()
        download_release_info()
        parse_release_info()
        topo_sorted_pacakge_list = build_dag()

        download_packages()
        compile_packages()

    def __load_bundle(self, scenario_name):
        self.__bundle_list = ['workarea', 'cepcsoft', 'external_release', 'external_common']

        install_root = self.__scenario['install_root']
        release_version = self.__scenario['release_version']
        workarea_root = self.__scenario['workarea']

        platform_root = os.path.join(install_root, self.__platform)
        external_common_root = os.path.join(platform_root, 'external')
        release_root = os.path.join(platform_root, 'release', release_version)
        external_release_root = os.path.join(release_root, 'external')
        cepcsoft_root = os.path.join(release_root, 'cepcsoft')

        self.__bundle_dict = {}
        self.__bundle_dict['cepcsoft'] = Bundle(cepcsoft_root)
        self.__bundle_dict['external_release'] = Bundle(external_release_root)
        self.__bundle_dict['external_common'] = Bundle(external_common_root)
        self.__bundle_dict['workarea'] = Bundle(workarea_root)
