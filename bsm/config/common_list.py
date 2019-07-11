import copy

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence

from bsm.util.config import dump_config

from bsm.config.util import config_from_file


class CommonList(MutableSequence):
    def __init__(self, *args, **kwargs):
        self.__data = []
        self.extend(list(*args, **kwargs))


    def __getitem__(self, index):
        return self.__data[index]

    def __setitem__(self, index, value):
        self.__data[index] = value

    def __delitem__(self, index):
        del self.__data[index]

    def __len__(self):
        return len(self.__data)

    def __repr__(self):
        return repr(self.__data)

    def insert(self, index, value):
        return self.__data.insert(index, value)


    def data(self):
        return self.__data

    def data_copy(self):
        return copy.deepcopy(self.__data)


    def load_from_file(self, config_file):
        self.__data = config_from_file(config_file, list)

    def save_to_file(self, config_file):
        dump_config(self.__data, config_file)
