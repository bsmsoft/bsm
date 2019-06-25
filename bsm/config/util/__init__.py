import os
import copy

from bsm.handler import HandlerNotFoundError

from bsm.util import expand_path
from bsm.util import ensure_list
from bsm.util import is_str

from bsm.util.config import load_config, ConfigError

from bsm.logger import get_logger
_logger = get_logger()

def _step_param(config_action):
    if not config_action:
        return None, {}

    if is_str(config_action):
        return config_action, {}

    if isinstance(config_action, dict):
        if len(config_action) > 1:
            _logger.warn('More than one actions found in the install action dictionary. Will only randomly choose one!')
            _logger.debug('config_action: {0}'.format(config_action))
        handler = next(iter(config_action))
        return handler, config_action[handler]

    return None, {}


class ConfigPackageError(Exception):
    pass

class ConfigPackageParamError(Exception):
    pass


def config_from_file(config_file):
    if not os.path.isfile(config_file):
        return {}

    try:
        loaded_data = load_config(config_file)
        if isinstance(loaded_data, dict):
            return loaded_data
        if loaded_data is not None:
            _logger.warn('Config file is not a dict, use empty dict instead: {0}'.format(config_file))
    except ConfigError as e:
        _logger.warn('Load config file failed, use empty dict instead: {0}'.format(config_file))

    return {}


def package_param_from_rel_dir(rel_dir, version_dir):
    frag = rel_dir.split(os.sep)
    if version_dir:
        if len(frag) < 3 or frag[-2] != 'versions':
            _logger.warn('Package config path is not valid: {0}'.format(rel_dir))
            raise ConfigPackageParamError
        version = frag[-1]
        frag = frag[:-2]
    else:
        if len(frag) < 2 or frag[-1] != 'head':
            _logger.warn('Package config path is not valid: {0}'.format(rel_dir))
            raise ConfigPackageParamError
        version = None
        frag = frag[:-1]

    package = frag[-1]

    frag = frag[:-1]
    if frag:
        subdir = os.path.join(*frag)
    else:
        subdir = ''

    return (subdir, package, version)


def package_param_from_identifier(identifier, pkg_cfg):
    frag = identifier.split(os.sep)

    # Use the last part as default package name
    if 'name' in pkg_cfg:
        pkg_name = pkg_cfg['name']
    elif frag[-1]:
        pkg_name = frag[-1]
    else:
        _logger.error('Package name not found for {0}'.format(identifier))
        raise ConfigPackageParamError

    frag = frag[:-1]

    # Use the first part as default category name
    if 'category' in pkg_cfg:
        category_name = pkg_cfg['category']
    elif len(frag) > 0:
        category_name = frag[0]
    else:
        _logger.warn('Category not specified for {0}'.format(identifier))
        raise ConfigPackageParamError

    frag = frag[1:]

    # Use the middle part as default subdir
    if 'subdir' in pkg_cfg:
        subdir = pkg_cfg['subdir']
    elif frag:
        subdir = os.path.join(*frag)
    else:
        subdir = ''

    return (category_name, subdir, pkg_name)


def transform_package(handler, trans_type, category, subdir, name, version, pkg_cfg, pkg_path,
        config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority):
    param = {}
    param['type'] = trans_type

    param['category'] = category
    param['subdir'] = subdir
    param['name'] = name
    param['version'] = version

    param['config_package'] = copy.deepcopy(pkg_cfg)
    param['package_path'] = copy.deepcopy(pkg_path)

    param['config_app'] = config_app.data_copy()
    param['config_output'] = config_output.data_copy()
    param['config_scenario'] = config_scenario.data_copy()
    param['config_option'] = config_option.data_copy()
    param['config_release_path'] = config_release_path.data_copy()
    param['config_attribute'] = config_attribute.data_copy()
    param['config_release'] = config_release.data_copy()
    param['config_release_install'] = config_release_install.data_copy()
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

def package_path(config_app, config_category, category, subdir, name, version):
    if category not in config_category:
        raise ConfigPackageError('Category not found: {0}'.format(category))

    ctg_cfg = config_category[category]

    if not ctg_cfg.get('root'):
        raise ConfigPackageError('Category root is not properly set for: {0}'.format(category))

    result = {}
    if ctg_cfg['version_dir']:
        result['main_dir'] = os.path.join(ctg_cfg['root'], subdir, name, version)
        result['work_dir'] = os.path.join(ctg_cfg['install_dir'], subdir, name, 'versions', version)
        result['config_dir'] = os.path.join(ctg_cfg['config_package_dir'], subdir, name, 'versions', version)
    else:
        result['main_dir'] = os.path.join(ctg_cfg['root'], subdir, name)
        result['work_dir'] = os.path.join(ctg_cfg['install_dir'], subdir, name, 'head')
        result['config_dir'] = os.path.join(ctg_cfg['config_package_dir'], subdir, name, 'head')
    result['misc_dir'] = os.path.join(result['work_dir'], 'misc')
    result['status_dir'] = os.path.join(result['work_dir'], 'status')
    result['status_install_file'] = os.path.join(result['status_dir'], 'install.yml')
    result['log_dir'] = os.path.join(result['work_dir'], 'log')
    result['config_file'] = os.path.join(result['config_dir'], config_app['config_package_file'])
    return result

def expand_package_path(package_main_dir, pkg_cfg):
    pkg_path = pkg_cfg.get('path', {})
    for k, v in pkg_path.items():
        pkg_path[k] = os.path.join(package_main_dir, v).rstrip(os.sep)

def expand_package_env(pkg_cfg):
    format_dict = {}
    format_dict['name'] = pkg_cfg['name']
    format_dict['category'] = pkg_cfg['category']
    format_dict['subdir'] = pkg_cfg['subdir']
    format_dict['version'] = pkg_cfg['version']
    format_dict.update(pkg_cfg.get('path', {}))

    env_prepend_path = pkg_cfg.get('env', {}).get('prepend_path', {})
    for k, v in env_prepend_path.items():
        result = []
        for i in ensure_list(v):
            result.append(i.format(**format_dict))
        env_prepend_path[k] = result

    env_append_path = pkg_cfg.get('env', {}).get('append_path', {})
    for k, v in env_append_path.items():
        result = []
        for i in ensure_list(v):
            result.append(i.format(**format_dict))
        env_append_path[k] = result

    env_set_env = pkg_cfg.get('env', {}).get('set_env', {})
    for k, v in env_set_env.items():
        env_set_env[k] = v.format(**format_dict)

    env_alias = pkg_cfg.get('env', {}).get('alias', {})
    for k, v in env_alias.items():
        env_alias[k] = v.format(**format_dict)

def install_status(status_install_file):
    return config_from_file(status_install_file)

def install_step(config_release_install, pkg_cfg, install_status, reinstall):
    result = {}

    for step in config_release_install['steps']:
        finished = install_status.get('steps', {}).get(step, {}).get('finished', False)
        install = reinstall or not finished

        config_action = ensure_list(pkg_cfg.get('install', {}).get(step, []))

        sub_index = 0
        for cfg_action in config_action:
            handler, param = _step_param(cfg_action)
            if handler:
                result.setdefault(step, [])
                result[step].append({'handler': handler, 'param': param, 'install': install})
                sub_index += 1

        if sub_index == 0:
            result.setdefault(step, [])
            result[step].append({'handler': '', 'param': {}, 'install': False})
            sub_index += 1

    return result

def find_top_priority(handler, category_priority, packages):
    if not packages:
        return None, None, None

    top_category = None
    for pkg in packages:
        if top_category is None or \
                (top_category not in category_priority and pkg[0] in category_priority) or \
                (top_category in category_priority and pkg[0] in category_priority and category_priority.index(pkg[0]) < category_priority.index(top_category)):
            top_category = pkg[0]
    packages = [p for p in packages if p[0] == top_category]

    top_version = None
    for pkg in packages:
        if top_version is None or handler.run('compare_version', pkg[2], top_version) > 0:
            top_version = pkg[2]
    packages = [p for p in packages if p[2] == top_version]

    # subdir is the least important
    top_subdir = None
    for pkg in packages:
        if top_subdir is None or pkg[1] < top_subdir:
            top_subdir = pkg[1]

    return top_category, top_subdir, top_version

def find_package(handler, category_priority, config_package, name, category=None, subdir=None, version=None):
    ''' Find the package with top priority matching the provided (category, subdir, version)
    '''
    packages = []

    for ctg in config_package:
        if category is not None and category != ctg:
            continue
        if ctg not in category_priority:
            continue
        for sd in config_package[ctg]:
            if subdir is not None and subdir != sd:
                continue
            if name not in config_package[ctg][sd]:
                continue
            for ver in config_package[ctg][sd][name]:
                if version is not None and version != ver:
                    continue
                packages.append((ctg, sd, ver))

    return find_top_priority(handler, category_priority, packages)

def load_packages(handler, category_priority, config_package):
    packages = {}

    for category in config_package:
        if category not in category_priority:
            continue
        for subdir in config_package[category]:
            for package in config_package[category][subdir]:
                for version in config_package[category][subdir][package]:
                    packages.setdefault(package, [])
                    packages[package].append((category, subdir, version))

    result = {}
    for package, value in packages.items():
        result[package] = find_top_priority(handler, category_priority, value)

    return result

def detect_category(config_category, directory):
    dir_expand = expand_path(directory)

    root_found = None
    category_found = None
    for ctg, cfg in config_category.items():
        if 'root' in cfg and dir_expand.startswith(cfg['root']):
            root_found = cfg['root']
            category_found = ctg
            break

    if category_found is None:
        return None, None

    rest_dir = dir_expand[len(root_found):].strip(os.sep)
    return category_found, rest_dir

def detect_package(directory, config_package):
    for category in config_package:
        for subdir in config_package[category]:
            for package in config_package[category][subdir]:
                for version, value in config_package[category][subdir][package].items():
                    if directory.startswith(value['package_path']['main_dir']):
                        return category, subdir, package, version
    return None, None, None, None

def check_conflict_package(directory, config_package):
    for category in config_package:
        for subdir in config_package[category]:
            for package in config_package[category][subdir]:
                for version, value in config_package[category][subdir][package].items():
                    if directory.startswith(value['package_path']['main_dir']) or value['package_path']['main_dir'].startswith(directory):
                        return category, subdir, package, version
    return None, None, None, None
