import click

from cepcenv import CepcEnvError

from cepcenv.util import expand_path

from cepcenv.config import load_config
from cepcenv.config import ConfigError

from cepcenv.shell import load_shell
from cepcenv.shell import ShellError

class CmdCommon(object):
    def __init__(self, config_file, verbose=False, shell_name=''):
        self.__config = {}

        if config_file:
            try:
                self.__config.update(load_config(expand_path(config_file)))
            except ConfigError as e:
                raise CepcEnvError('Can not load config: %s' % e)

        # The final verbose value: self._config['verbose'] || verbose
        if ('verbose' not in self.__config) or (not self.__config['verbose']):
            self.__config['verbose'] = verbose

        self.__shell = None
        if shell_name:
            try:
                self.__shell = load_shell(shell_name)()
            except ShellError as e:
                raise CepcEnvError('Can not load shell: %s' % e)

    def _config(self):
        return self.__config

    def _shell(self):
        if not self.__shell:
            raise CepcEnvError('No shell specified')
        return self.__shell
