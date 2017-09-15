from cepcenv.util import is_str

__VERSION_ITEMS = ('release_root', 'release_status_root',
        'external_common_root', 'external_release_root', 'cepcsoft_root', 'work_root',
        'release_info', 'version', 'release_repo',
        'platform', 'os', 'arch', 'compiler')


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
            version_config['version'] = version_name

    return version_config


def load_version_config(config, version_name=None, version_config_cmd={}):
    version_config = __filter_version_config(config)
    version_config.update(__version_config_specific(config, version_name))
    version_config.update(__filter_version_config(version_config_cmd))

    return version_config
