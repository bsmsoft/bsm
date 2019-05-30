import os
import copy

from bsm.config.common import Common

from bsm.logger import get_logger
_logger = get_logger()


class Install(Common):
    def load(self, config_release, config_category):
        for ctg, ctg_cfg in config_category.items():
            if ctg_cfg['install']:
                self[ctg] = {}

        config_release_package = config_release.get('package', {})
        for pkg_path, pkg_cfg in config_release_package.items():
            frag = pkg_path.split(os.sep)

            if 'category' in pkg_cfg:
                category_name = pkg_cfg['category']
            elif len(frag) > 1:
                category_name = frag[0]
            else:
                _logger.warn('Category not specified for {0}'.format(pkg_path))
                continue

            if category_name not in self:
                continue

            if 'name' in pkg_cfg:
                pkg_name = pkg_cfg['name']
            elif frag[-1]:
                pkg_name = frag[-1]
            else:
                _logger.error('Package name not found for {0}'.format(pkg_path))
                continue

            self[category_name][pkg_name] = copy.deepcopy(pkg_cfg)
