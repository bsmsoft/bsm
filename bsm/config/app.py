from bsm import BSM_HOME

class App(object):
    def __init__(self, config):
        self.__config = config

        self.__load_bsm()
        self.__set_default()

    def __load_bsm(self):
        if 'id' in self.__config:
            return
        self.__config['id'] = 'bsm'
        self.__config['name'] = 'BSM'
        self.__config['description'] = 'Bundled Software Manager'

    def __set_default(self):
        app_id = self.__config['id']

        self.__config.setdefault('description', 'Application of BSM')
        self.__config.setdefault('site', 'https://bsmhep.github.io/')

        self.__config.setdefault('command', app_id)
        self.__config.setdefault('gittemp', '')
        self.__config.setdefault('logger_name', 'BSM')
        self.__config.setdefault('env_prefix', app_id.upper()+'_')
        self.__config.setdefault('user_config_file', '~/.'+app_id+'.conf')
        self.__config.setdefault('user_info_file', '~/.'+app_id+'.info')
        self.__config.setdefault('example_config_user', os.path.join(BSM_HOME, 'support', 'bsm.conf.example'))
        self.__config.setdefault('release_collection_dir', '.bsm')
        self.__config.setdefault('package_info_dir', '.bsm')

        self.__config.setdefault('default_release_repo', 'https://github.com/bsmhep/bsmdemo')
        self.__config.setdefault('default_software_root', os.getcwd())
