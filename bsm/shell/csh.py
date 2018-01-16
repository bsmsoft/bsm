import sys
import os

from bsm.shell.base import Base

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
CSH_INIT = os.path.join(CUR_DIR, 'bsm.csh')
CSH_SCRIPT_INIT = os.path.join(CUR_DIR, 'bsm_script.csh')

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

    def define_bsm(self):
        python_exe = sys.executable or 'python'

        common_alias = '''\
alias {0} '\
set _bsm_python_exe="{1}"; \
set _bsm_argv="\!*"; \
source "{2}"; \
unset _bsm_argv; \
unset _bsm_python_exe; \
eval "exit $_bsm_exit"\
';
'''

        bsm_alias = common_alias.format('bsm', python_exe, CSH_INIT)
        bsm_script_alias = common_alias.format('bsm_script', python_exe, CSH_SCRIPT_INIT)

        return bsm_alias + bsm_script_alias

    def undefine_bsm(self):
        bsm_exit = '''\
unalias bsm_script;
unalias bsm;
'''
        return bsm_exit
