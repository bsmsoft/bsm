from cepcenv.config import load_config
from cepcenv.config import dump_config
from cepcenv.config import ConfigError

from cepcenv.util import expand_path

from cepcenv.logger import get_logger
_logger = get_logger()

class Info(object):
    def __init__(self, info_file='~/.cepcenv.info'):
        self.__info_file = expand_path(info_file)

        self.__load_info()

    def __load_info(self):
        try:
            self.__info = load_config(self.__info_file)
        except ConfigError as e:
            self.__info = {}
            _logger.debug('Load info file "{0}" error: {1}'.format(self.__info_file, e))

    def __save_info(self):
        dump_config(self.__info, self.__info_file)

    def set_default_version(self, version):
        self.__info['default'] = version
        self.__save_info()

    @property
    def default_version(self):
        return self.__info.get('default')
