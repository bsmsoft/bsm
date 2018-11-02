import os

from bsm.config.common import Common

from bsm import BSM_HOME

class App(Common):
    def load_app(self):
        self.__load_bsm()
        self.__set_default()

    def __load_bsm(self):
        if 'id' in self:
            return
        self['id'] = 'bsm'
        self['name'] = 'BSM'
        self['description'] = 'Bundled Software Manager'

    def __set_default(self):
        app_id = self['id']

        self.setdefault('description', 'Application of BSM')
        self.setdefault('site', 'https://bsmhep.github.io/')

        self.setdefault('command', app_id)
        self.setdefault('env_prefix', app_id.upper())
        self.setdefault('config_user_file', '~/.'+app_id+'.conf')
        self.setdefault('config_info_file', '~/.'+app_id+'.info')
        self.setdefault('example_config_user', os.path.join(BSM_HOME, 'support', 'bsm.conf.example'))
        self.setdefault('release_dir', '.bsm')
        self.setdefault('package_work_dir', '.bsm')
        self.setdefault('solo_env', {})
        self.setdefault('path_env', {})
        self.setdefault('alias', {})

        self.setdefault('release_repo', 'https://github.com/bsmhep/bsmdemo')
        self.setdefault('software_root', os.getcwd())

        self.setdefault('gittemp', '')
