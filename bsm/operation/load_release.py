from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LoadRelease(Base):
    def execute(self):
        self._env.load_release(self._config['scenario'], self._config['release'])
