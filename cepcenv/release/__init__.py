
class ReleaseError(Exception):
    pass

class ReleaseVersionNotExistError(ReleaseError):
    pass


class Release(object):
    def __init__(self, method):
        self.__method = method
        self.__load()

    def __load(self):
        self.__method.

    def __load_from_dir(self):
        self.__release_config = {}

        for k in ['version', 'info', 'package', 'attribute', 'install']:
            try:
                self.__release_config[k] = load_config(os.path.join(dir_name, 'config', k+'.yml'))
            except ConfigError as e:
                print(e)
                pass

    def __copy_handler_from_dir(self):
        pass

    def config(self):
        pass

    def install_handler(self):
        pass
