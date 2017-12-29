import sys

from cepcenv.shell.base import Base

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

    def define_cepcenv(self):
        python_exe = sys.executable or 'python'

        cepcenv_func = '''\
cepcenv() {{
  local _check_shell="$('{python_exe}' -c 'from cepcenv import main;main(check_shell=True)' $* 2>/dev/null)"

  if [ "$_check_shell" = 'CEPCENV:OUTPUT_IS_SHELL' ]; then
    local _script="$('{python_exe}' -c 'from cepcenv import main;main()' --shell sh $*)"
    local _exit_code=$?
    [ $_exit_code -eq 0 ] && eval "$_script"
  else
    '{python_exe}' -c 'from cepcenv import main;main()' $*
    local _exit_code=$?
  fi

  return "$_exit_code"
}}

cepcenv_script() {{
  local _check_shell="$('{python_exe}' -c 'from cepcenv import main;main(check_shell=True)' $* 2>/dev/null)"

  if [ "$_check_shell" = 'CEPCENV:OUTPUT_IS_SHELL' ]; then
    '{python_exe}' -c 'from cepcenv import main;main()' --shell sh $*
  else
    >&2 echo 'This command does not output shell script'
    return 2
  fi
}}
'''.format(python_exe=python_exe)

        return cepcenv_func

    def undefine_cepcenv(self):
        cepcenv_exit = '''\
unset -f cepcenv_script
unset -f cepcenv
'''
        return cepcenv_exit
