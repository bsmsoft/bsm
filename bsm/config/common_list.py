import copy

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence


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
