from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class Exit(Base):
    def execute(self):
        self._env.unload_packages()
        self._env.unload_release()
        self._env.unload_app()

        self._config.reset(initial_env=self._env.env_final())
