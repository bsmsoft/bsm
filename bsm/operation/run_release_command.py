from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class RunReleaseCommand(Base):
    def execute(self, command):
        param = {}

        param['command'] = command.copy()

        for n in [
                'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
                'release_setting', 'release_package', 'category', 'category_priority',
                'packages_install', 'packages_install_path',
                'packages_runtime', 'packages_runtime_path', 'packages_check']:
            param['prop_'+n] = self._prop[n].data_copy()

        with Handler(self._prop['release_path']['handler_python_dir']) as h:
            try:
                return h.run('command', param)
            except HandlerNotFoundError:
                _logger.error('Could not find out how to run command: %s', command)
                raise
