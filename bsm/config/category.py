from bsm.config.common import Common

from bsm.env import Env as BsmEnv

def _load_category(ctg, cfg, config_app, config_scenario):
    result = {}
    result['name'] = ctg
    result['pre_check'] = cfg.get('pre_check', False)
    result['install'] = cfg.get('install', False)
    result['auto_env'] = cfg.get('auto_env', False)
    result['version_dir'] = cfg.get('version_dir', False)
    result['share_env'] = cfg.get('share_env', False)

    if 'root' not in cfg:
        result['install'] = False
        result['auto_env'] = False
        result['share_env'] = False
        return result

    result['root'] = cfg['root'].format(config_scenario)

    result['work_dir'] = os.path.join(result['root'], config_app['category_work_dir'])
    if result['share_env']:
        result['config_package_dir'] = os.path.join(result['work_dir'], 'shared')
    else:
        result['config_package_dir'] = os.path.join(result['work_dir'], 'version', config_scenario['version'])

    return result

class Category(Common):
    def load(self, config_app, config_scenario, config_release):
        for ctg, cfg in config_release.get('setting', {}).get('categories', {}).items():
            self[ctg] = _load_category(ctg, cfg, config_app, config_scenario)
