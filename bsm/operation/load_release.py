from bsm.operation import Base

class LoadRelease(Base):
    def execute(self):
        self._env.load_release(
            self._prop['scenario'], self._prop['option_release'], self._prop['release_setting'])
        self._prop.reset(initial_env=self._env.env_final())
