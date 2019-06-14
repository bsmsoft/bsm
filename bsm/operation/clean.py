from bsm.operation import Base

class Clean(Base):
    def execute(self):
        self._env.unload_packages()
        self._env.unload_release()

        self._config.reset(initial_env=self._env.env_final())
