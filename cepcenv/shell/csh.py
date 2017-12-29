import sys
import os

from cepcenv.shell.base import Base

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
CSH_INIT = os.path.join(CUR_DIR, 'cepcenv.csh')
CSH_SCRIPT_INIT = os.path.join(CUR_DIR, 'cepcenv_script.csh')

class Csh(Base):
    def echo(self, content):
        lines = content.rstrip().split('\n')

        # "\" should be escaped
        # "'" will be converted into four chars "'\''"
        newlines = map(lambda x:'echo \'' + x.replace('\\', '\\\\').replace('\'', '\'\\\'\'') + '\'', lines)

        return ';\n'.join(newlines) + ';\n'

    def set_env(self, env_name, env_value):
        return 'setenv {0} "{1}";\n'.format(env_name, env_value)

    def unset_env(self, env_name):
        return 'unsetenv {0};\n'.format(env_name)

    def source(self, script_path):
        return 'source {0};\n'.format(script_path)

    def define_cepcenv(self):
        python_exe = sys.executable or 'python'

        common_alias = '''\
alias {0} '\
set _cepcenv_python_exe="{1}"; \
set _cepcenv_argv="\!*"; \
source "{2}"; \
unset _cepcenv_argv; \
unset _cepcenv_python_exe; \
eval "exit $_cepcenv_exit"\
';
'''

        cepcenv_alias = common_alias.format('cepcenv', python_exe, CSH_INIT)
        cepcenv_script_alias = common_alias.format('cepcenv_script', python_exe, CSH_SCRIPT_INIT)

        return cepcenv_alias + cepcenv_script_alias

    def undefine_cepcenv(self):
        cepcenv_exit = '''\
unalias cepcenv_script;
unalias cepcenv;
'''
        return cepcenv_exit
