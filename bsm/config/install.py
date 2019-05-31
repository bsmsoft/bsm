import os
import copy

from bsm.config.common import Common

from bsm.logger import get_logger
_logger = get_logger()


class Install(Common):
    def load(self, config_app, config_scenario, config_release_path, config_attribute, config_release, config_category):
        category_priority = config_release.get('setting', {}).get('category_priority', [])

        for ctg, ctg_cfg in config_category.items():
            if ctg_cfg['install']:
                self[ctg] = {}

        sys.path.insert(0, config_release_path['handler_python_dir'])

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

            self[pkg_name] = {}
            self[pkg_name]['category'] = category_name

            param = {}
            param['action'] = 'install'
            param['name'] = pkg_name
            param['category'] = category_name
            param['package'] = copy.deepcopy(pkg_cfg)
            param['config_app'] = config_app.data_copy
            param['config_scenario'] = config_scenario.data_copy
            param['config_release_path'] = config_release_path.data_copy
            param['config_attribute'] = config_attribute.data_copy
            param['config_release'] = config_release.data_copy
            param['config_category'] = config_category.data_copy
            try:
                with Handler() as h:
                    result = h.run('transform_package', param)
                    if isinstance(result, dict):
                        self[pkg_name]['config'] = result
            except HandlerNotFoundError as e:
                _logger.debug('Transformer for package not found: {0}'.format(e))
                self[pkg_name]['config'] = copy.deepcopy(pkg_cfg)
            except Exception as e:
                _logger.error('Transformer for package run error: {0}'.format(e))
                raise
            self[pkg_name]['config'] = copy.deepcopy(pkg_cfg)

            self[pkg_name]['step'] = copy.deepcopy(pkg_cfg)

        sys.path.remove(config_release_path['handler_python_dir'])
