import os


BSM_HOME = os.path.dirname(os.path.realpath(__file__))

# This name is very long in order to avoid conflicts with other modules
HANDLER_MODULE_NAME = '_bsm_handler_run_avoid_conflict'


with open(os.path.join(BSM_HOME, 'BSM_VERSION'), 'r') as f:
    BSM_VERSION = f.read().strip()


from bsm.config import Config
from bsm.env import Env

from bsm.git import Git
from bsm.git import GitNotFoundError
from bsm.git import GitEmptyUrlError

from bsm.logger import add_stream_logger


class BSM(object):
    def __init__(self, config_entry={}):
        self.__config_entry = config_entry

        self.__config = Config(self.__config_entry)

        self.__initialize_logger()

        self.__env = Env()

    def __initialize_logger(self):
        add_stream_logger(self.__config['output']['verbose'])

    @staticmethod
    def version():
        return BSM_VERSION

    @staticmethod
    def home():
        return BSM_HOME

    def reload(self, config_entry, update_config=False):
        if update_config:
            self.__config_entry.update(config_entry)
        else:
            self.__config_entry = config_entry

        self.__config = Config(self.__config_entry)

    def app(self):
        return self.__config['app']['id']

    def init_script(self, shell):
        pass

    def exit_script(self, shell):
        pass

    def config(self, config_type, scenario=None):
        if scenario:
            self.reload({'scenario': scenario}, True)
        return dict(self.__config[config_type])

    def config_user_example(self):
        pass

    def ls_remote(self):
        try:
            git = Git()
            tags = git.ls_remote_tags(self.__config['scenario']['release_repo'])
        except GitNotFoundError:
            _logger.error('Git is not found. Please install "git" first')
            raise
        except GitEmptyUrlError:
            _logger.error('No release repository found. Please setup "release_repo" first')
            raise

        versions = [tag[1:] for tag in tags if tag.startswith(b'v')]
        versions.sort()

        return versions

    def install(self):
        pass

    def ls(self):
        pass

    def use(self):
        self.__env.update()

    def env(self):
        pass

    def ls_package(self):
        pass

    def default_load(self, shell=None):
        pass
