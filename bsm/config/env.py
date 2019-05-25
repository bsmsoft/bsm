from bsm.config.common import Common

from bsm.env import Env

class Env(Common):
    def load_env(self, initial_env, env_prefix):
        env = Env(initial_env, env_prefix)
