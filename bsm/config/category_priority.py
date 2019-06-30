import os

from collections import OrderedDict

from bsm.config.common_list import CommonList

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class CategoryPriority(CommonList):
    def __init__(self, config_user, config_scenario, config_release, config_category):
        super(CategoryPriority, self).__init__()

        self.__update_priority(config_release.get('setting', {}), config_category)

        self.__update_priority(config_user, config_category)

        if config_scenario.get('scenario'):
            self.__update_priority(config_user.get('scenario', {}).get(config_scenario['scenario'], {}), config_category)

        self.__remove_duplicated_priority()

    def __update_priority(self, config_container, config_category):
        priority = ensure_list(config_container.get('category_priority', []))
        priority = [ctg for ctg in priority if ctg in config_category]
        priority += [ctg for ctg in config_container.get('category', {}) if ctg not in priority]

        # prepend the new priority to the beginning
        self[:0] = priority

    def __remove_duplicated_priority(self):
        new_list = OrderedDict.fromkeys(self)
        del self[:]
        self.extend(new_list)
