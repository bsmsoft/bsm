import copy

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence

from bsm.util.config import dump_config

from bsm.prop.util import prop_from_file


class Common(object):
    def __init__(self):
        self.__data = None

    def data(self):
        return self.__data

    def data_copy(self):
        return copy.deepcopy(self.__data)

    def load_from_file(self, config_file):
        self.__data = prop_from_file(config_file, list)

    def save_to_file(self, config_file):
        dump_config(self.__data, config_file)
