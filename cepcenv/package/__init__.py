class Package(object):
    def __init__(self, name):
        self.__name = name

    def is_ready(self, action):
        pass

    def save_action_status(self, action, start, end):
        pass
