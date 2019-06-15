from bsm.operation import Base

class LoadRelease(Base):
    def execute(self):
        self._env.load_release(self._config['scenario'], self._config['option'], self._config['release'])
        self._config.reset(initial_env=self._env.env_final())
