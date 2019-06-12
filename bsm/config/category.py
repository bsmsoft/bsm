import os

from bsm.config.common import Common

class Category(Common):
    def __init__(self, config_app, config_scenario, config_release):
        super(Category, self).__init__()

        for ctg, ctg_cfg in config_release.get('setting', {}).get('categories', {}).items():
            self.__load_category(ctg, ctg_cfg, config_app, config_scenario)

    def __load_category(self, ctg, ctg_cfg, config_app, config_scenario):
        self[ctg] = {}
        self[ctg]['name'] = ctg
        self[ctg]['pre_check'] = ctg_cfg.get('pre_check', False)
        self[ctg]['install'] = ctg_cfg.get('install', False)
        self[ctg]['auto_env'] = ctg_cfg.get('auto_env', False)
        self[ctg]['version_dir'] = ctg_cfg.get('version_dir', False)
        self[ctg]['share_env'] = ctg_cfg.get('share_env', False)

        if 'root' not in ctg_cfg:
            self[ctg]['install'] = False
            self[ctg]['auto_env'] = False
            self[ctg]['share_env'] = False
            return

        self[ctg]['root'] = ctg_cfg['root'].format(**config_scenario)

        self[ctg]['work_dir'] = os.path.join(self[ctg]['root'], config_app['category_work_dir'])
        if self[ctg]['share_env']:
            self[ctg]['config_package_dir'] = os.path.join(self[ctg]['work_dir'], 'shared')
        else:
            self[ctg]['config_package_dir'] = os.path.join(self[ctg]['work_dir'], 'release', config_scenario['version'])
        self[ctg]['install_dir'] = os.path.join(self[ctg]['work_dir'], 'install')
