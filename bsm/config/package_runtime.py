from bsm.config.common import Common

from bsm.util import walk_rel_dir

from bsm.logger import get_logger
_logger = get_logger()

class PackageRuntime(Common):
    def load(self, config_app, config_release, config_category):
        category_priority = config_release.get('setting', {}).get('category_priority', [])
        category_runtime = [ctg for ctg in category_priority if config_category.get(ctg, {}).get('root')]
        category_runtime += [ctg for ctg, cfg in config_category.items() if ctg not in category_runtime and cfg.get('root')]

        _logger.debug('Category for runtime: {0}'.format(category_runtime))

        for category in category_runtime:
            config_package_dir = config_category[category]['config_package_dir']

            for full_path, rel_dir, f in walk_rel_dir(config_package_dir):
                if f != config_app['config_package_file']:
                    continue
                pkg_name = os.path.splitext(f)[0]
                self['package'][os.path.join(rel_dir, pkg_name)] = load_config(full_path)
                package


            self[category][subdir][package][version] = {}
