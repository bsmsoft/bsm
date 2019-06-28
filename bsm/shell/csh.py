import sys
import os

from bsm.shell.base import Base

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
CSH_INIT = os.path.join(CUR_DIR, 'bsm.csh')

class Csh(Base):
    def comment(self, content):
        return '\n'

    def echo(self, content):
        lines = content.rstrip().split('\n')

        # "\" should be escaped
        # "'" will be converted into four chars "'\''"
        newlines = map(lambda x:'echo \'' + x.replace('\\', '\\\\').replace('\'', '\'\\\'\'') + '\'', lines)

        return ';\n'.join(newlines) + ';\n'

    def set_env(self, env_name, env_value):
        return 'setenv {0} \'{1}\';\n'.format(env_name, env_value)

    def unset_env(self, env_name):
        return 'unsetenv {0};\n'.format(env_name)

    def alias(self, alias_name, alias_value):
        return 'alias {0} \'{1}\';\n'.format(alias_name, alias_value)

    def unalias(self, alias_name):
        return 'unalias {0};\n'.format(alias_name)

    def source(self, script_path):
        return 'source {0};\n'.format(script_path)

    def script_init(self):
        python_exe = sys.executable or 'python'

        bsm_alias = '''\
alias {cmd_name} '\
set _bsm_python_exe="{python_exe}"; \
set _bsm_argv="\!*"; \
set _bsm_cmd_name="{cmd_name}"; \
set _bsm_app_root="{app_root}"; \
source "{csh_init}"; \
unset _bsm_app_root; \
unset _bsm_cmd_name; \
unset _bsm_argv; \
unset _bsm_python_exe; \
eval "exit $_bsm_exit"\
';
'''.format(cmd_name=self._cmd_name, python_exe=python_exe, app_root=self._app_root, csh_init=CSH_INIT)

        return bsm_alias

    def script_exit(self):
        bsm_exit = '''\
unalias {cmd_name};
'''.format(cmd_name=self._cmd_name)
        return bsm_exit
