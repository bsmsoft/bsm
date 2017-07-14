from cepcenv.shell import Shell

class Csh(Shell):
    def set_env(self, env_name, env_value):
        return 'setenv %s "%s"\n' % (env_name, env_value)

    def source(self, script_path):
        return 'source %s\n' % script_path

    def define_cepcenv(self):
        return 'cepcenv() not implemented\n'
