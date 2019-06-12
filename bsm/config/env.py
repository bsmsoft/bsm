from bsm.config.common import Common

from bsm.env import Env as BsmEnv

class Env(Common):
    def __init__(self, initial_env, env_prefix):
        super(Env, self).__init__()

        env = BsmEnv(initial_env, env_prefix)
        self.update(env.current_release())
