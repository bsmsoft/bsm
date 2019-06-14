import os
import copy

from bsm.handler import HandlerNotFoundError

from bsm.util import ensure_list
from bsm.util import is_str

from bsm.util.config import load_config, ConfigError

from bsm.logger import get_logger
_logger = get_logger()


def _config_from_file(config_file):
    try:
        loaded_data = load_config(config_file)
        if isinstance(loaded_data, dict):
            return loaded_data
        else:
            _logger.warn('Config file is not a dict: {0}'.format(config_file))
            _logger.warn('Use empty dict instead')
    except ConfigError as e:
        return dict()

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


def transform_package(handler, operation, category, subdir, name, version, pkg_cfg,
        config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_category):
    param = {}
    param['operation'] = operation

    param['category'] = category
    param['subdir'] = subdir
    param['name'] = name
    param['version'] = version

    param['config_package'] = copy.deepcopy(pkg_cfg)
    param['config_app'] = config_app.data_copy()
    param['config_output'] = config_output.data_copy()
    param['config_scenario'] = config_scenario.data_copy()
    param['config_option'] = config_option.data_copy()
    param['config_release_path'] = config_release_path.data_copy()
    param['config_attribute'] = config_attribute.data_copy()
    param['config_release'] = config_release.data_copy()
    param['config_category'] = config_category.data_copy()

    try:
        result = handler.run('transform_package', param)
        if isinstance(result, dict):
            return result
    except HandlerNotFoundError:
        _logger.debug('Transformer for package not found')
    except Exception as e:
        _logger.error('Transformer for package run error: {0}'.format(e))
        raise

    return copy.deepcopy(pkg_cfg)

def package_path(config_app, config_category, pkg_cfg):
    result = {}
    ctg_cfg = config_category['content'][pkg_cfg['category']]
    if ctg_cfg['version_dir']:
        result['main_dir'] = os.path.join(ctg_cfg['root'], pkg_cfg['subdir'], pkg_cfg['name'], pkg_cfg['version'])
        result['work_dir'] = os.path.join(ctg_cfg['install_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'versions', pkg_cfg['version'])
        result['config_dir'] = os.path.join(ctg_cfg['config_package_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'versions', pkg_cfg['version'])
    else:
        result['main_dir'] = os.path.join(ctg_cfg['root'], pkg_cfg['subdir'], pkg_cfg['name'])
        result['work_dir'] = os.path.join(ctg_cfg['install_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'head')
        result['config_dir'] = os.path.join(ctg_cfg['config_package_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'head')
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
    return _config_from_file(status_install_file)

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
