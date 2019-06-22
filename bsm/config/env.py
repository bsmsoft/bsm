from bsm.env import Env as BsmEnv

from bsm.config.common_dict import CommonDict

class Env(CommonDict):
    def __init__(self, initial_env, env_prefix):
        super(Env, self).__init__()

        env = BsmEnv(initial_env, env_prefix)
        self.update(env.current_release())
