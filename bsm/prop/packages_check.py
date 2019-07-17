import copy

from bsm.handler import Handler, HandlerNotFoundError

from bsm.error import PropPackageParamError

from bsm.prop.util import package_param_from_identifier

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


def _transform_package(handler, ctg, name, pkg_prop, prop):
    param = {}
    param['type'] = 'check'

    param['category'] = ctg
    param['name'] = name

    param['prop_package'] = copy.deepcopy(pkg_prop)

    for n in [
            'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
            'release_setting', 'release_package', 'category', 'category_priority']:
        param['prop_'+n] = prop[n].data_copy()

    try:
        result = handler.run('transform.package', param)
        if isinstance(result, dict):
            return result
    except HandlerNotFoundError:
        _logger.debug('Transformer for package not found')
    except Exception as e:
        _logger.error('Transformer for package run error: %s', e)
        raise

    return copy.deepcopy(pkg_prop)


class PackagesCheck(CommonDict):
    def __init__(self, prop):
        super(PackagesCheck, self).__init__()

        category_check = [
            ctg for ctg, ctg_prop in prop['category'].items() if ctg_prop.get('pre_check')]

        _logger.debug('Category for check: %s', category_check)

        with Handler(prop['release_path']['handler_python_dir']) as h:
            for identifier, pkg_prop in prop['release_package'].items():
                try:
                    category_name, _, pkg_name = package_param_from_identifier(identifier, pkg_prop)
                except PropPackageParamError:
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
                final_props = self[category_name][pkg_name]

                final_props['prop_origin'] = copy.deepcopy(pkg_prop)

                final_props['prop'] = _transform_package(
                    h, category_name, pkg_name, pkg_prop, prop)
                final_props['prop']['name'] = pkg_name
                final_props['prop']['category'] = category_name
