from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class Use(Base):
    def execute(self, without_package):
        self._env.load_release(self._config['scenario'], self._config['release'])
        if without_package:
            return
#        self._env.load_package()
