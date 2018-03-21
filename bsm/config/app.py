from bsm import BSM_HOME

class App(object):
    def __init__(self):
        self.__config = {}

    def __load_bsm(self):
        self.__config['name'] = 'bsm'
        self.__config['description'] = 'Bundled Software Manager'

    def __set_default(self):
        name = self.__config['name']
        self.__config.setdefault('description', 'Application of BSM')
        self.__config.setdefault('site', 'https://bsmhep.github.io/')
        self.__config.setdefault('command_name', name)
        self.__config.setdefault('user_config_file', '~/.'+name+'.conf')
        self.__config.setdefault('release_repo', 'https://github.com/bsmhep/bsmdemo')
        self.__config.setdefault('example_config_user', os.path.join(BSM_HOME, 'support', 'bsm.conf.example'))
        self.__config.setdefault('release_collection_dir', '.bsm')
        self.__config.setdefault('package_info_dir', '.bsm')
