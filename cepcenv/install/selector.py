# TODO: add this priority mechanism
PRIORITY_LIST = ['INSTALL', 'EXTRACT', 'POST_CHECK', 'PRE_CHECK', 'DOWNLOAD']

class Selector(object):
    def __init__(self, config, release_config):
        self.__config = config
        self.__release_config = release_config

        self.__max_total = 8
        self.__max_extract = 2
        self.__max_install = 2

    def select(self, running, idle):
        running_total = 0
        running_extract = 0
        running_install = 0
        for v in running:
            running_total += 1
            if v[1] == 'EXTRACT':
                running_extract += 1
            if v[1] == 'INSTALL':
                running_install += 1

        idle_extract = [v for v in idle if v[1] == 'EXTRACT']
        idle_install = [v for v in idle if v[1] == 'INSTALL']

        selected = []

        for v in idle_install:
            if running_install < self.__max_install and running_total < self.__max_total:
                selected.append(v)
                running_install += 1
                running_total += 1

        for v in idle_extract:
            if running_extract < self.__max_extract and running_total < self.__max_total:
                selected.append(v)
                running_extract += 1
                running_total += 1

        for v in idle:
            if v not in idle_install and v not in idle_extract and running_total < self.__max_total:
                selected.append(v)
                running_total += 1

        return selected
