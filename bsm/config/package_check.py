import copy

from bsm.handler import Handler, HandlerNotFoundError

from bsm.config.util import ConfigPackageParamError
from bsm.config.util import package_param_from_identifier

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


def _transform_package(handler, ctg, name, pkg_cfg, config):
    param = {}
    param['type'] = 'check'

    param['category'] = ctg
    param['name'] = name

    param['config_package'] = copy.deepcopy(pkg_cfg)

    for n in [
            'app', 'output', 'scenario', 'option', 'release_path', 'attribute',
            'release', 'release_package', 'category', 'category_priority']:
        param['config_'+n] = config[n].data_copy()

    try:
        result = handler.run('transform.package', param)
        if isinstance(result, dict):
            return result
    except HandlerNotFoundError:
        _logger.debug('Transformer for package not found')
    except Exception as e:
        _logger.error('Transformer for package run error: %s', e)
        raise

    return copy.deepcopy(pkg_cfg)


class PackageCheck(CommonDict):
    def __init__(self, config):
        super(PackageCheck, self).__init__()

        category_check = [
            ctg for ctg, ctg_cfg in config['category'].items() if ctg_cfg.get('pre_check')]

        _logger.debug('Category for check: %s', category_check)

        with Handler(config['release_path']['handler_python_dir']) as h:
            for identifier, pkg_cfg in config['release_package'].items():
                try:
                    category_name, _, pkg_name = package_param_from_identifier(identifier, pkg_cfg)
                except ConfigPackageParamError:
                    continue

                if category_name not in category_check:
                    _logger.debug('Package "%s" could not be checked with category "%s"',
                                  pkg_name, category_name)
                    continue

                self.setdefault(category_name, {})
                if pkg_name in self[category_name]:
                    _logger.warning('Duplicated package found: category "%s", package "%s"',
                                    category_name, pkg_name)
                self[category_name].setdefault(pkg_name, {})
                final_config = self[category_name][pkg_name]

                final_config['config_origin'] = copy.deepcopy(pkg_cfg)

                final_config['config'] = _transform_package(
                    h, category_name, pkg_name, pkg_cfg, config)
                final_config['config']['name'] = pkg_name
                final_config['config']['category'] = category_name
