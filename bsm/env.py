import os
import sys
import json

from bsm.const import BSMCLI_CMD


def _parse_path(path_str):
    return path_str.split(os.pathsep)

def _emit_path(path_list):
    return os.pathsep.join(path_list)

def _parse_info(info_str):
    return json.loads(info)

def _emit_info(info):
    return json.dumps(info, separators=(',',':'))


class Env(object):
    def __init__(self, initial_env=None, env_prefix='BSM'):
        if initial_env is None:
            initial_env = os.environ

        self.__env = initial_env.copy()
        self.__old_env = self.__env.copy()
        self.__unalias = []
        self.__alias = {}

        self.__init_env_name(env_prefix)

        self.__init_bsmcli_bin()

    def __init_env_name(self, env_prefix):
        self.__env_name = {}

        self.__env_name['bsmcli_bin']      = env_prefix + '_BSMCLI_BIN'

        self.__env_name['app_info']        = env_prefix + '_APP_INFO'

        self.__env_name['software_root']   = env_prefix + '_SOFTWARE_ROOT'
        self.__env_name['release_version'] = env_prefix + '_RELEASE_VERSION'
        self.__env_name['release_info']    = env_prefix + '_RELEASE_INFO'
        self.__env_name['packages_info']   = env_prefix + '_PACKAGES_INFO'

    def __init_bsmcli_bin(self):
        if not sys.executable:
            self.__bsmcli_bin = BSMCLI_CMD
            return

        python_bin_dir = os.path.dirname(sys.executable)
        self.__bsmcli_bin = os.path.join(python_bin_dir, BSMCLI_CMD)

    def __merge_path(self, env_name, path_list, append=False):
        original_path_list = []
        if env_name in self.__env:
            original_path_list = _parse_path(self.__env[env_name])

        if append:
            final_path_list = original_path_list + path_list
        else:
            final_path_list = path_list + original_path_list

        self.__env[env_name] = _emit_path(final_path_list)

    def __remove_path(self, env_name, path_list):
        if env_name not in self.__env:
            return

        original_path_list = _parse_path(self.__env[env_name])

        final_path_list = [x for x in original_path_list if x not in [path_list]]

        if not final_path_list:
            del self.__env[env_name]
        else:
            self.__env[env_name] = _emit_path(final_path_list)

    def __load_env(self, config_env):
        env_info = {}
        env_info['set_env'] = []
        env_info['path'] = {}
        env_info['alias'] = []

        if 'unset_env' in config_env:
            unset_env = ensure_list(config_env['unset_env'])
            for e in unset_env:
                if e in self.__env:
                    del self.__env[e]

        if 'set_env' in config_env:
            for e, v in config_env['set_env'].items():
                self.__env[e] = v
                env_info['set_env'].append(e)

        if 'prepend_path' in config_env:
            for e, v in config_env['prepend_path'].items():
                path_list = ensure_list(v)
                self.__merge_path(e, path_list)
                env_info['path'].setdefault(e, [])
                env_info['path'][e] += path_list

        if 'append_path' in config_env:
            for e, v in config_env['append_path'].items():
                path_list = ensure_list(v)
                self.__merge_path(e, path_list, True)
                env_info['path'].setdefault(e, [])
                env_info['path'][e] += path_list

        if 'unalias' in config_env:
            unalias_list = ensure_list(config_env['unalias'])
            for e in unalias_list:
                if e in self.__alias:
                    del self.__alias[e]
                else:
                    self.__unalias.append(e)

        if 'alias' in config_env:
            self.__alias.update(config_env['alias'])
            env_info['alias'] += list(config_env['alias'].keys())

        return env_info

    def __unload_env(self, env_info):
        if 'set_env' in env_info:
            for e in env_info['set_env']:
                if e in self.__env:
                    del self.__env[e]

        if 'path' in env_info:
            for e, v in env_info['path'].items():
                self.__remove_path(e, v)

        if 'alias' in env_info:
            for e in env_info['alias']:
                if e in self.__alias:
                    del self.__alias[e]
                else:
                    self.__unalias.append(e)

    def load_app(self, config_app):
        self.__env[self.__env_name['bsmcli_bin']] = self.__bsmcli_bin

        env_info = self.__load_env(config_app['env'])
        app_info = {}
        app_info['env'] = env_info
        self.__env[self.__env_name['app_info']] = _emit_info(app_info)

    def unload_app(self):
        if self.__env_name['bsmcli_bin'] in self.__env:
            del self.__env[self.__env_name['bsmcli_bin']]

        if self.__env_name['app_info'] in self.__env:
            app_info = _parse_info(self.__env[self.__env_name['app_info']])
            self.__unload_env(app_info.get('env', {}))
            del self.__env[self.__env_name['app_info']]

    def env_final(self):
        return self.__env.copy()

    def apply_changes(self):
        self.__old_env = self.__env.copy()
        self.__alias = {}
        return {'set_env': {}, 'unset_env': [], 'alias': {}, 'unalias': []}
