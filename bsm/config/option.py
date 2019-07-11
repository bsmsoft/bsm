from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class Option(CommonDict):
    def __init__(self, config):
        super(Option, self).__init__()

        self.__update_option(config['release_status'])

        self.__update_option(config['user'])

        if config['scenario'].get('scenario'):
            self.__update_option(config['user'].get('scenario', {}).get(config['scenario']['scenario'], {}))

        if config['entry'].get('default_scenario') and config['info'].get('default', {}).get('scenario'):
            self.__update_option(config['info'].get('default', {}))
        else:
            self.__update_option(config['env'])

        self.__update_option(config['entry'])

        self.__check_option(config['option_list'])

    def __update_option(self, config_container):
        if 'option' not in config_container:
            return

        option = config_container['option']
        if isinstance(option, dict):
            self.update(option)

    def __check_option(self, config_option_list):
        for k, v in self.items():
            if k not in config_option_list:
                _logger.warning('Option "{0}" is not in the option list'.format(k))
