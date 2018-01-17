import sys

from bsm.shell.base import Base

class Sh(Base):
    def echo(self, content):
        lines = content.rstrip().split('\n')

        # "\" should be escaped
        # "'" will be converted into four chars "'\''"
        newlines = map(lambda x:'echo \'' + x.replace('\\', '\\\\').replace('\'', '\'\\\'\'') + '\'', lines)

        return '\n'.join(newlines) + '\n'

    def set_env(self, env_name, env_value):
        return 'export {0}="{1}"\n'.format(env_name, env_value)

    def unset_env(self, env_name):
        return 'unset {0}\n'.format(env_name)

    def source(self, script_path):
        return '. {0}\n'.format(script_path)

    def define_bsm(self):
        python_exe = sys.executable or 'python'

        bsm_func = '''\
bsm() {{
  local _check_shell="$('{python_exe}' -c 'from bsm import main;main(check_shell=True)' $* 2>/dev/null)"

  if [ "$_check_shell" = 'BSM:OUTPUT_IS_SHELL' ]; then
    local _script="$('{python_exe}' -c 'from bsm import main;main()' --shell sh $*)"
    local _exit_code=$?
    [ $_exit_code -eq 0 ] && eval "$_script"
  else
    '{python_exe}' -c 'from bsm import main;main()' $*
    local _exit_code=$?
  fi

  return "$_exit_code"
}}

bsm_script() {{
  local _check_shell="$('{python_exe}' -c 'from bsm import main;main(check_shell=True)' $* 2>/dev/null)"

  if [ "$_check_shell" = 'BSM:OUTPUT_IS_SHELL' ]; then
    '{python_exe}' -c 'from bsm import main;main()' --shell sh $*
  else
    >&2 echo 'This command does not output shell script'
    return 2
  fi
}}
'''.format(python_exe=python_exe)

        return bsm_func

    def undefine_bsm(self):
        bsm_exit = '''\
unset -f bsm_script
unset -f bsm
'''
        return bsm_exit
