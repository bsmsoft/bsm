import time
import random

class Executor(object):
    def __init__(self, config, release_config):
        self.__config = config
        self.__release_config = release_config

    def param(self, vertex):
        return vertex

    def execute(self, param_vertex):
        if param_vertex[1] == 'DOWNLOAD':
            time.sleep(random.randrange(2, 5))
        elif param_vertex[1] == 'INSTALL':
            time.sleep(random.randrange(3, 6))
        else:
            time.sleep(random.randrange(0, 2))
        return None

    def report(self, vertex, result):
        if isinstance(result, Exception):
            print('Vertex {0} finished with exception: {1}'.format(vertex, result))
        else:
            print('Vertex {0} finished with result: {1}'.format(vertex, result))

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
