class Config(object):
    def __init__(self):
        pass

    @property
    def app(self):
        return self.__app

    @property
    def user(self):
        return self.__app

    @property
    def release(self):
        return self.__app

    @property
    def package(self, name):
        return self.__app
