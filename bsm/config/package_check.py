import copy

from bsm.handler import Handler, HandlerNotFoundError

from bsm.config.util import ConfigPackageParamError
from bsm.config.util import package_param_from_identifier, transform_package

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class PackageCheck(CommonDict):
    def __init__(self, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority):
        super(PackageCheck, self).__init__()

        category_check = [ctg for ctg, ctg_cfg in config_category.items() if ctg_cfg.get('pre_check')]

        _logger.debug('Category for check: {0}'.format(category_check))

        with Handler(config_release_path['handler_python_dir']) as h:
            for identifier, pkg_cfg in config_release.get('package', {}).items():
                try:
                    category_name, subdir, pkg_name = package_param_from_identifier(identifier, pkg_cfg)
                except ConfigPackageParamError:
                    continue

                if category_name not in category_check:
                    _logger.debug('Package "{0}" could not be checked with category "{1}"'.format(pkg_name, category_name))
                    continue

                self.setdefault(category_name, {})
                if pkg_name in self[category_name]:
                    _logger.warn('Duplicated package found: category({0}), package({1})'.format(category_name, pkg_name))
                self[category_name].setdefault(pkg_name, {})
                final_config = self[category_name][pkg_name]

                final_config['config_origin'] = copy.deepcopy(pkg_cfg)

                final_config['config'] = self.__transform_package(h, category_name, pkg_name, pkg_cfg,
                        config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_category, config_category_priority)
                final_config['config']['name'] = pkg_name
                final_config['config']['category'] = category_name

    def __transform_package(self, handler, category, name, pkg_cfg,
            config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_category, config_category_priority):
        param = {}
        param['type'] = 'check'

        param['category'] = category
        param['name'] = name

        param['config_package'] = copy.deepcopy(pkg_cfg)

        param['config_app'] = config_app.data_copy()
        param['config_output'] = config_output.data_copy()
        param['config_scenario'] = config_scenario.data_copy()
        param['config_option'] = config_option.data_copy()
        param['config_release_path'] = config_release_path.data_copy()
        param['config_attribute'] = config_attribute.data_copy()
        param['config_release'] = config_release.data_copy()
        param['config_category'] = config_category.data_copy()
        param['config_category_priority'] = config_category_priority.data_copy()

        try:
            result = handler.run('transform.package', param)
            if isinstance(result, dict):
                return result
        except HandlerNotFoundError:
            _logger.debug('Transformer for package not found')
        except Exception as e:
            _logger.error('Transformer for package run error: {0}'.format(e))
            raise

        return copy.deepcopy(pkg_cfg)
