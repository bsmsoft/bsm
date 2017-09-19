import random
import string
import datetime

from cepcenv.util import expand_path

from cepcenv.sw import Platform

from cepcenv.config.util import load_config
from cepcenv.config.version import load_version_config
from cepcenv.config.release import load_release_config
from cepcenv.config.release import ReleaseVersionMismatchError


__TEMP_VERSION_PREFIX = ''
__TEMP_VERSION_LENGTH = 6

__DEFAULT_RELEASE_REPO = 'https://github.com/cepc/cepcsoft'

__DEFAULT_ROOT = {
        'external_common_root': '{release_root}/{platform}/external',
        'external_release_root': '{release_root}/{platform}/release/{version}/external',
        'cepcsoft_root': '{release_root}/{platform}/release/{version}/cepcsoft',
        'release_status_root': '{release_root}/{platform}/release/{version}/_cepcenv',
}


def load_main(options_common):
    config = {}

    config_file = options_common['config_file']
    if config_file:
        try:
            c = load_config(expand_path(config_file))
            if not isinstance(c, dict):
                c = {}
            config.update(c)
        except Exception as e:
#            print('Can not load config: {0}'.format(e))
            pass

    # The final verbose value: config['verbose'] || verbose
    if ('verbose' not in config) or (not config['verbose']):
        config['verbose'] = options_common['verbose']

    return config


def __temp_version():
    return __TEMP_VERSION_PREFIX \
            + datetime.datetime.utcnow().strftime('%Y%m%d_%H.%M.%S_%f') + '_' \
            + ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(__TEMP_VERSION_LENGTH))


def __validate_release_version(version_config, release_config):
    if 'version' in release_config and 'version' in version_config:
        if  version_config['version'] != release_config['version']:
            raise ReleaseVersionMismatchError('Release version "{0}" and "{1}" do not match'.format(
                version_config['version'], release_config['version']))

    elif 'version' in release_config and 'version' not in version_config:
        version_config['version'] = release_config['version']

    elif 'version' not in release_config and 'version' in version_config:
        release_config['version'] = version_config['version']

    elif 'version' not in release_config and 'version' not in version_config:
        release_config['version'] = __temp_version()
        version_config['version'] = release_config['version']

def __process_platform(version_config):
    sp = Platform(version_config.get('arch'), version_config.get('os'), version_config.get('compiler'))
    if 'arch' not in version_config or not version_config['arch']:
        version_config['arch'] = sp.arch
    if 'os' not in version_config or not version_config['os']:
        version_config['os'] = sp.os
    if 'compiler' not in version_config or not version_config['compiler']:
        version_config['compiler'] = sp.compiler
    if 'platform' not in version_config or not version_config['platform']:
        version_config['platform'] = sp.platform

def __process_release_root(version_config):
    for k, v in __DEFAULT_ROOT.items():
        if k not in version_config:
            version_config[k] = v

def __format_release_root(version_config):
    for r in __DEFAULT_ROOT:
        version_config[r] = expand_path(version_config[r].format(**version_config))

def __process_config(version_config, release_config):
    __process_platform(version_config)

    if 'release_repo' not in version_config or not version_config['release_repo']:
        version_config['release_repo'] = __DEFAULT_RELEASE_REPO

    __validate_release_version(version_config, release_config)

    __process_release_root(version_config)
    __format_release_root(version_config)


def load_version(config, version_name=None, version_config_cmd={}):
    version_config = load_version_config(config, version_name, version_config_cmd)
    release_config = load_release_config(version_config)
    __process_config(version_config, release_config)
    return version_config, release_config
