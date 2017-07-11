from cepcenv.shell.base import Base

class Csh(Base):
    def set_env(self, env_name, env_value):
        return 'setenv %s "%s"\n' % (env_name, env_value)

    def source(self, script_path):
        return 'source %s\n' % script_path
