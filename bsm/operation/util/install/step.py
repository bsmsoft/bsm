from bsm.package_manager import PackageManager

from bsm.util import is_str
from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class InstallStepError(Exception):
    pass


def _step_param(config_action):
    if not config_action:
        return None, None

    if is_str(config_action):
        return config_action, None

    if isinstance(config_action, dict):
        if len(config_action) > 1:
            _logger.warn('More than one actions found in the install action dictionary. Will only randomly choose one!')
            _logger.debug('config_action: {0}'.format(config_action))
        handler = next(iter(config_action))
        return handler, config_action[handler]

    return None, None


class Step(object):
    def __init__(self, config_version, config_release):
        self.__config_version = config_version
        self.__config_release = config_release

        self.__load_setting()
        self.__load_steps()

    def __load_setting(self):
        setting_install = self.__config_release.get('setting', {}).get('install', {})
        self.__all_steps = setting_install.get('steps', [])
        self.__atomic_start = setting_install.get('atomic_start')
        self.__atomic_end = setting_install.get('atomic_end')
        self.__no_skip = ensure_list(setting_install.get('no_skip', []))

        if len(self.__all_steps) != len(set(self.__all_steps)):
            raise InstallStepError('Duplicated steps found: {0}'.format(self.__all_steps))

        if self.__atomic_start not in self.__all_steps or self.__atomic_end not in self.__all_steps:
            raise InstallStepError('Can not find atomic start/end: {0}/{1}'.format(self.__atomic_start, self.__atomic_end))

        if self.__all_steps.index(self.__atomic_start) > self.__all_steps.index(self.__atomic_end):
            raise InstallStepError('atomic_start should not be after atomic_end')

    def __load_steps(self):
        self.__steps = {}

        pkg_mgr = PackageManager(self.__config_version, self.__config_release)

        for pkg, pkg_info in pkg_mgr.package_all().items():
            if not pkg_info.get('config_category', {}).get('install'):
                continue

            self.__steps[pkg] = []

            for action in self.__all_steps:
                if not pkg_info.get('config', {}).get('install', {}).get(action):
                    continue

                if action not in self.__no_skip and pkg_mgr.is_finished(pkg, action):
                    continue

                config_action = ensure_list(pkg_info['config']['install'][action])

                sub_index = 0
                for cfg_action in config_action:
                    handler, param = _step_param(cfg_action)
                    if handler:
                        self.__steps[pkg].append({'action': action, 'sub_action': sub_index, 'handler': handler, 'param': param})
                    sub_index += 1

    def package_steps_all(self):
        return self.__steps

    def package_step(self, pkg, action, sub_action):
        for step in self.__steps.get(pkg, []):
            if step['action'] == action and step['sub_action'] == sub_action:
                return step
        return {}

    def is_last_sub_action(self, pkg, action, sub_action):
        sub_action_max = -1
        for step in self.__steps.get(pkg, []):
            if step['action'] == action and step['sub_action'] > sub_action_max:
                sub_action_max = step['sub_action']
        return sub_action >= sub_action_max


    def __search_step(self, action, step_list):
        for step in step_list:
            if action == step['action']:
                return step
        return None

    def __find_dest_action(self, all_steps, step_list, dest_start, dest_end):
        start_found = False
        for step in all_steps:
            if not start_found and step == dest_start:
                start_found = True
            if start_found:
                step = self.__search_step(step, step_list)
                if step:
                    return step
            if step == dest_end:
                break
        return None

    def find_atomic_start(self, pkg):
        if pkg not in self.__steps:
            return None
        return self.__find_dest_action(self.__all_steps, self.__steps[pkg], self.__atomic_start, self.__atomic_end)

    def find_atomic_end(self, pkg):
        if pkg not in self.__steps:
            return None
        return self.__find_dest_action(reversed(self.__all_steps), reversed(self.__steps[pkg]), self.__atomic_end, self.__atomic_start)
