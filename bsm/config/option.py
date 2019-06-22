from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class Option(CommonDict):
    def __init__(self, config_entry, config_info, config_env, config_user, config_scenario, config_release_status, config_option_list):
        super(Option, self).__init__()

        self.__update_option(config_release_status)

        self.__update_option(config_user)

        if config_scenario.get('scenario'):
            self.__update_option(config_user.get('scenario', {}).get(config_scenario['scenario'], {}))

        if config_entry.get('default_scenario') and config_info.get('default', {}).get('scenario'):
            self.__update_option(config_info.get('default', {}))
        else:
            self.__update_option(config_env)

        self.__update_option(config_entry)

        self.__check_option(config_option_list)

    def __update_option(self, config_container):
        if 'option' not in config_container:
            return

        option = config_container['option']
        if isinstance(option, dict):
            self.update(option)

    def __check_option(self, config_option_list):
        for k, v in self.items():
            if k not in config_option_list:
                _logger.warn('Option "{0}" is not in the option list'.format(k))
