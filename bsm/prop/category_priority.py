from collections import OrderedDict

from bsm.prop.common_list import CommonList

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class CategoryPriority(CommonList):
    def __init__(self, prop):
        super(CategoryPriority, self).__init__()

        self.__update_priority(prop['release_setting'], prop['category'])

        self.__update_priority(prop['user'], prop['category'])

        if prop['scenario'].get('scenario'):
            self.__update_priority(
                prop['user'].get('scenario', {}).get(prop['scenario']['scenario'], {}),
                prop['category'])

        self.__remove_duplicated_priority()

    def __update_priority(self, prop_container, prop_category):
        priority = ensure_list(prop_container.get('category_priority', []))
        priority = [ctg for ctg in priority if ctg in prop_category]
        priority += [ctg for ctg in prop_container.get('category', {}) if ctg not in priority]

        # prepend the new priority to the beginning
        self[:0] = priority

    def __remove_duplicated_priority(self):
        new_list = OrderedDict.fromkeys(self)
        del self[:]
        self.extend(new_list)
