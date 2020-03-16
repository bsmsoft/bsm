from bsm.util import is_str

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class Option(CommonDict):
    def __init__(self, option_type, prop):
        super(Option, self).__init__()

        self.__option_type = option_type
        self.__option_list = prop['option_list']

        self.__update_option(prop['user'])

        if prop['scenario'].get('scenario'):
            self.__update_option(
                prop['user'].get('scenario', {}).get(prop['scenario']['scenario'], {}))

        if (prop['entry'].get('default_scenario') and
                prop['info'].get('default', {}).get('scenario')):
            self.__update_option(prop['info'].get('default', {}))
        else:
            self.__update_option(prop['env'])

        self.__update_option(prop['entry'])

    def __update_option(self, prop_container):
        if 'option' not in prop_container:
            return

        option = prop_container['option']
        if isinstance(option, dict):
            for k, v in option.items():
                if k in self.__option_list.get(self.__option_type, {}):
                    self[k] = self.__option_value(k, v)

    def __option_value(self, key, value):
        var_type = self.__option_list[self.__option_type][key][0]

        if var_type.lower() in ['bool', 'boolean']:
            if is_str(value):
                if value.lower() in ['false', 'f', 'no', 'n', '0', '']:
                    return False
                return True
            return bool(value)

        if var_type.lower() in ['int', 'integer']:
            try:
                return int(value)
            except ValueError:
                _logger.error('Not a valid int option value: %s', value)
                return 0

        return value
