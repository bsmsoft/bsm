from util import expand_path

class ReleaseVersionMismatchError(Exception):
    pass


class Manager(object):
    def __init__(self, config):
        self.__config = config

    def install(self, scenario_config):
        if 'release_config' in scenario_config and scenario_config['release_config']:
            release_config = load_config(expand_path(scenario_config['release_config']))

            if 'release_version' in release_config:
                version_in_release = release_config['release_version']

                if 'release_version' in scenario_config:
                    version_in_scenario = scenario_config['release_version']
                    if version_in_scenario != version_in_release:
                        raise ReleaseVersionMismatchError('Version "{0}" and "{1}" do not match'.format(version_in_scenario, version_in_release))
                else:
                    scenario_config['release_version'] = version_in_scenario

        release_config = None

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
