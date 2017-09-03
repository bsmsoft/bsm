from cepcenv.util import is_str
from cepcenv.software_platform import SoftwarePlatform

__VERSION_ITEMS = ('release_root', 'release_version', 'release_info', 'release_repo', 'workarea', 'platform', 'os', 'arch', 'compiler')

__DEFAULT_RELEASE_REPO = 'https://github.com/cepc/cepcsoft'


def __filter_version_config(config):
    version_config = {}

    for k, v in config.items():
        if k in __VERSION_ITEMS and v is not None:
            version_config[k] = v

    return version_config

def __version_config_specific(config, version_name):
    version_config = {}

    if is_str(version_name):
        if 'versions' in config and version_name in config['versions']:
            version_config = __filter_version_config(config['versions'][version_name])
        else:
            version_config['release_version'] = version_name

    return version_config


def load_version(config, version_name=None, version_config_cmd={}):
    version_config = __filter_version_config(config)
    version_config.update(__version_config_specific(config, version_name))
    version_config.update(__filter_version_config(version_config_cmd))

    sp = SoftwarePlatform(version_config.get('arch'), version_config.get('os'), version_config.get('compiler'))
    if 'arch' not in version_config or not version_config['arch']:
        version_config['arch'] = sp.arch
    if 'os' not in version_config or not version_config['os']:
        version_config['os'] = sp.os
    if 'compiler' not in version_config or not version_config['compiler']:
        version_config['compiler'] = sp.compiler
    if 'platform' not in version_config or not version_config['platform']:
        version_config['platform'] = sp.platform

    if 'release_repo' not in version_config or not version_config['release_repo']:
        version_config['release_repo'] = __DEFAULT_RELEASE_REPO

    return version_config
