import os

from bsm import BSM_HOME
from bsm.config.common import Common
from bsm.util import expand_path

class App(Common):
    def load_app(self, app_root):
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
        self.setdefault('site', 'https://bsmhep.github.io/')

        self.setdefault('cmd_name', app_id)
        self.setdefault('version_pattern', 'v(.*)')
        self.setdefault('env_prefix', app_id.upper())
        self.setdefault('config_user_file', '~/.'+app_id+'.conf')
        self.setdefault('config_info_file', '~/.'+app_id+'.info')
        self.setdefault('release_dir_name', '.bsm')
        self.setdefault('package_work_dir_name', '.bsm')
        self.setdefault('set_env', {})
        self.setdefault('prepend_path', {})
        self.setdefault('append_path', {})
        self.setdefault('unset_env', [])
        self.setdefault('alias', {})
        self.setdefault('unalias', [])

        self.setdefault('release_repo', 'https://github.com/bsmhep/bsmdemo')
        self.setdefault('software_root', os.getcwd())

#        self.setdefault('git_temp', '')

        if 'example_config_user' in self and 'app_root' in self:
            self['example_config_user'] = os.path.join(self['app_root'], self['example_config_user'])
        else:
            self['example_config_user'] = os.path.join(BSM_HOME, 'support', 'bsm.conf.example')
