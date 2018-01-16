# TODO: add this priority mechanism
PRIORITY_LIST = ('compile', 'extract', 'post_compile', 'pre_compile', 'download', 'clean')

class Selector(object):
    def __init__(self, config, release_config):
        self.__config = config
        self.__release_config = release_config

        self.__max_total = 8
        self.__max_extract = 4
        self.__max_compile = 1

    def select(self, running, idle):
        running_total = 0
        running_extract = 0
        running_compile = 0
        for v in running:
            running_total += 1
            if v[1] == 'extract':
                running_extract += 1
            if v[1] == 'compile':
                running_compile += 1

        idle_extract = [v for v in idle if v[1] == 'extract']
        idle_compile = [v for v in idle if v[1] == 'compile']

        selected = []

        for v in idle_compile:
            if running_compile < self.__max_compile and running_total < self.__max_total:
                selected.append(v)
                running_compile += 1
                running_total += 1

        for v in idle_extract:
            if running_extract < self.__max_extract and running_total < self.__max_total:
                selected.append(v)
                running_extract += 1
                running_total += 1

        for v in idle:
            if v not in idle_compile and v not in idle_extract and running_total < self.__max_total:
                selected.append(v)
                running_total += 1

        return selected
