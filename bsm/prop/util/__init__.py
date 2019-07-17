import os
import copy

from bsm.error import ConfigLoadError
from bsm.error import PropPackageError
from bsm.error import PropPackageParamError

from bsm.handler import HandlerNotFoundError

from bsm.util import expand_path
from bsm.util import ensure_list
from bsm.util import is_str

from bsm.util.config import load_config

from bsm.logger import get_logger
_logger = get_logger()

def _step_param(prop_action):
    if not prop_action:
        return None, {}

    if is_str(prop_action):
        return prop_action, {}

    if isinstance(prop_action, dict):
        if len(prop_action) > 1:
            _logger.warning(
                'More than one actions found in the install action dictionary. '
                'Will only randomly choose one!')
            _logger.debug('prop_action: %s', prop_action)
        handler = next(iter(prop_action))
        return handler, prop_action[handler]

    return None, {}


def prop_from_file(config_file, config_type=dict):
    if not os.path.isfile(config_file):
        return config_type()

    try:
        loaded_data = load_config(config_file)
        if isinstance(loaded_data, config_type):
            return loaded_data
        if loaded_data is not None:
            _logger.warning(
                'Config file is not a %s, use empty value instead: %s',
                config_type.__name__, config_file)
    except ConfigLoadError:
        _logger.warning(
            'Load config file failed, use empty %s instead: %s', config_type.__name__, config_file)

    return config_type()


def package_param_from_rel_dir(rel_dir, version_dir):
    frag = rel_dir.split(os.sep)
    if version_dir:
        if len(frag) < 3 or frag[-2] != 'versions':
            _logger.warning('Package prop path is not valid: %s', rel_dir)
            raise PropPackageParamError
        version = frag[-1]
        frag = frag[:-2]
    else:
        if len(frag) < 2 or frag[-1] != 'head':
            _logger.warning('Package prop path is not valid: %s', rel_dir)
            raise PropPackageParamError
        version = None
        frag = frag[:-1]

    package = frag[-1]

    frag = frag[:-1]
    if frag:
        subdir = os.path.join(*frag)
    else:
        subdir = ''

    return (subdir, package, version)


def package_param_from_identifier(identifier, pkg_prop):
    frag = identifier.split(os.sep)

    # Use the last part as default package name
    if 'name' in pkg_prop:
        pkg_name = pkg_prop['name']
    elif frag[-1]:
        pkg_name = frag[-1]
    else:
        _logger.error('Package name not found for %s', identifier)
        raise PropPackageParamError

    frag = frag[:-1]

    # Use the first part as default category name
    if 'category' in pkg_prop:
        category_name = pkg_prop['category']
    elif frag:
        category_name = frag[0]
    else:
        _logger.warning('Category not specified for %s', identifier)
        raise PropPackageParamError

    frag = frag[1:]

    # Use the middle part as default subdir
    if 'subdir' in pkg_prop:
        subdir = pkg_prop['subdir']
    elif frag:
        subdir = os.path.join(*frag)
    else:
        subdir = ''

    return (category_name, subdir, pkg_name)


def transform_package(handler, trans_type,
                      ctg, subdir, name, version, pkg_prop, pkg_path, prop):
    param = {}
    param['type'] = trans_type

    param['category'] = ctg
    param['subdir'] = subdir
    param['name'] = name
    param['version'] = version

    param['prop'] = copy.deepcopy(pkg_prop)
    param['package_path'] = copy.deepcopy(pkg_path)

    for n in ['app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
              'release_setting', 'release_package', 'release_install',
              'category', 'category_priority']:
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

def package_path(prop_app, prop_category, category, subdir, name, version):
    if category not in prop_category:
        raise PropPackageError('Category not found: {0}'.format(category))

    ctg_prop = prop_category[category]

    if not ctg_prop.get('root'):
        raise PropPackageError('Category root is not properly set for: {0}'.format(category))

    result = {}
    if ctg_prop['version_dir']:
        result['main_dir'] = os.path.join(ctg_prop['root'], subdir, name, version)
        result['work_dir'] = os.path.join(ctg_prop['ctrl_install_dir'],
                                          subdir, name, 'versions', version)
        result['prop_dir'] = os.path.join(ctg_prop['ctrl_package_dir'],
                                          subdir, name, 'versions', version)
    else:
        result['main_dir'] = os.path.join(ctg_prop['root'], subdir, name)
        result['work_dir'] = os.path.join(ctg_prop['ctrl_install_dir'], subdir, name, 'head')
        result['prop_dir'] = os.path.join(ctg_prop['ctrl_package_dir'], subdir, name, 'head')
    result['misc_dir'] = os.path.join(result['work_dir'], 'misc')
    result['status_dir'] = os.path.join(result['work_dir'], 'status')
    result['status_install_file'] = os.path.join(result['status_dir'], 'install.yml')
    result['log_dir'] = os.path.join(result['work_dir'], 'log')
    result['prop_file'] = os.path.join(result['prop_dir'], prop_app['package_prop_file'])
    return result

def expand_package_path(package_main_dir, pkg_prop):
    pkg_path = pkg_prop.get('path', {})
    for k, v in pkg_path.items():
        pkg_path[k] = os.path.join(package_main_dir, v).rstrip(os.sep)

def expand_package_env(pkg_prop):
    format_dict = {}
    format_dict['name'] = pkg_prop['name']
    format_dict['category'] = pkg_prop['category']
    format_dict['subdir'] = pkg_prop['subdir']
    format_dict['version'] = pkg_prop['version']
    format_dict.update(pkg_prop.get('path', {}))

    env_prepend_path = pkg_prop.get('env', {}).get('prepend_path', {})
    for k, v in env_prepend_path.items():
        result = []
        for i in ensure_list(v):
            result.append(i.format(**format_dict))
        env_prepend_path[k] = result

    env_append_path = pkg_prop.get('env', {}).get('append_path', {})
    for k, v in env_append_path.items():
        result = []
        for i in ensure_list(v):
            result.append(i.format(**format_dict))
        env_append_path[k] = result

    env_set_env = pkg_prop.get('env', {}).get('set_env', {})
    for k, v in env_set_env.items():
        env_set_env[k] = v.format(**format_dict)

    env_alias = pkg_prop.get('env', {}).get('alias', {})
    for k, v in env_alias.items():
        env_alias[k] = v.format(**format_dict)

def install_status(status_install_file):
    return prop_from_file(status_install_file)

def install_step(prop_release_install, pkg_prop, inst_status, reinstall):
    result = {}

    for step in prop_release_install['steps']:
        finished = inst_status.get('steps', {}).get(step, {}).get('finished', False)
        install = reinstall or not finished

        prop_actions = ensure_list(pkg_prop.get('install', {}).get(step, []))

        sub_index = 0
        for prop_action in prop_actions:
            handler, param = _step_param(prop_action)
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
        if top_category is None:
            top_category = pkg[0]
            continue
        if pkg[0] not in category_priority:
            continue
        if top_category not in category_priority:
            top_category = pkg[0]
            continue
        if category_priority.index(pkg[0]) < category_priority.index(top_category):
            top_category = pkg[0]
    packages = [p for p in packages if p[0] == top_category]

    top_version = None
    for pkg in packages:
        if top_version is None or handler.run('version_compare', pkg[2], top_version) > 0:
            top_version = pkg[2]
    packages = [p for p in packages if p[2] == top_version]

    # subdir is the least important
    top_subdir = None
    for pkg in packages:
        if top_subdir is None or pkg[1] < top_subdir:
            top_subdir = pkg[1]

    return top_category, top_subdir, top_version

def find_package(handler, category_priority, prop_packages, name, category=None, subdir=None, version=None):
    ''' Find the package with top priority matching the provided (category, subdir, version)
    '''
    packages = []

    for ctg in prop_packages:
        if category is not None and category != ctg:
            continue
        if ctg not in category_priority:
            continue
        for subd in prop_packages[ctg]:
            if subdir is not None and subdir != subd:
                continue
            if name not in prop_packages[ctg][subd]:
                continue
            for ver in prop_packages[ctg][subd][name]:
                if version is not None and version != ver:
                    continue
                packages.append((ctg, subd, ver))

    return find_top_priority(handler, category_priority, packages)

def load_packages(handler, category_priority, prop_packages):
    packages = {}

    for category in prop_packages:
        if category not in category_priority:
            continue
        for subdir in prop_packages[category]:
            for package in prop_packages[category][subdir]:
                for version in prop_packages[category][subdir][package]:
                    packages.setdefault(package, [])
                    packages[package].append((category, subdir, version))

    result = {}
    for package, value in packages.items():
        result[package] = find_top_priority(handler, category_priority, value)

    return result

def detect_category(prop_category, directory):
    dir_expand = expand_path(directory)

    root_found = None
    category_found = None
    for ctg, prop in prop_category.items():
        if 'root' in prop and dir_expand.startswith(prop['root']):
            root_found = prop['root']
            category_found = ctg
            break

    if category_found is None:
        return None, None

    rest_dir = dir_expand[len(root_found):].strip(os.sep)
    return category_found, rest_dir

def detect_package(directory, prop_packages):
    for category in prop_packages:
        for subdir in prop_packages[category]:
            for package in prop_packages[category][subdir]:
                for version, value in prop_packages[category][subdir][package].items():
                    if directory.startswith(value['package_path']['main_dir']):
                        return category, subdir, package, version
    return None, None, None, None

def check_conflict_package(directory, prop_packages):
    for category in prop_packages:
        for subdir in prop_packages[category]:
            for package in prop_packages[category][subdir]:
                for version, value in prop_packages[category][subdir][package].items():
                    if directory.startswith(value['package_path']['main_dir']) or value['package_path']['main_dir'].startswith(directory):
                        return category, subdir, package, version
    return None, None, None, None
