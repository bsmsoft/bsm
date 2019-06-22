import os

from bsm import BSM_HOME
from bsm.config.common_dict import CommonDict
from bsm.util import expand_path

class App(CommonDict):
    def __init__(self, app_root):
        super(App, self).__init__()

        if app_root:
            self.__load_app_root(expand_path(app_root))
        self.__load_bsm_default()
        self.__set_default()

    def __load_app_root(self, app_root):
        self['app_root'] = app_root
        self.update_from_file(os.path.join(app_root, 'main.yml'))
        self.update_from_file(os.path.join(app_root, 'extra.yml'))

    def __load_bsm_default(self):
        if 'id' in self:
            return
        self['id'] = 'bsm'
        self['name'] = 'BSM'
        self['description'] = 'Bundled Software Manager'

    def __set_default(self):
        app_id = self['id']

        self.setdefault('description', 'Application of BSM')
        self.setdefault('site', 'https://bsmsoft.github.io/')

        self.setdefault('cmd_name', app_id)
        self.setdefault('version_pattern', '^v(.*)$')
        self.setdefault('version_stable_pattern', '^v(\d+\.\d+\.\d+)$')
        self.setdefault('env_prefix', app_id.upper())
        self.setdefault('config_user_file', '~/.'+app_id+'.conf')
        self.setdefault('config_info_file', '~/.'+app_id+'.info')
        self.setdefault('release_work_dir', '.bsm')
        self.setdefault('category_work_dir', '.bsm')
        self.setdefault('config_package_file', 'package.yml')
        self.setdefault('env', {})

        self.setdefault('release_repo', 'https://github.com/bsmsoft/bsmdemo')
        self.setdefault('software_root', '~/bsmdemo')

        if 'example_config_user' in self and 'app_root' in self:
            self['example_config_user'] = os.path.join(self['app_root'], self['example_config_user'])
        else:
            self['example_config_user'] = os.path.join(BSM_HOME, 'support', 'bsm.conf.example')
