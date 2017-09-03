from cepcenv.util import ensure_list

from cepcenv.release import Release

from cepcenv.install import Install


class Manager(object):
    def __init__(self, config, version_config):
        self.__config = config
        self.__version_config = version_config

    def install(self):
        release = Release(self.__version_config)

        install = Install(self.__config, release.config)

        install.run()

    def __load_bundle(self, version_name):
        self.__bundle_list = ['workarea', 'cepcsoft', 'external_release', 'external_common']

        install_root = self.__version['install_root']
        release_version = self.__version['release_version']
        workarea_root = self.__version['workarea']

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
