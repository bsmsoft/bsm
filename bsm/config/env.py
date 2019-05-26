from bsm.config.common import Common

from bsm.env import Env as BsmEnv

class Env(Common):
    def load(self, initial_env, env_prefix):
        env = BsmEnv(initial_env, env_prefix)
