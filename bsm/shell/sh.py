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

    def init_script(self, command):
        python_exe = sys.executable or 'python'

        bsm_func = '''\
{command}() {{
  _command_result=$('{python_exe}' -c 'from bsm.cli import main;main(cmd_name='{command}',output_for_shell=True)' "$*")
  if [ $? -eq 0 ]; then
    echo "$_command_result" | '{python_exe}' -c 'from bsm.shell import main;main(shell_name='sh',command='{command}')'
    return $?
  else
    return 1
  fi

  _{command}_bsm_exit_code=$?
  if [ $_{command}_bsm_exit_code -eq 0 ]; then
    echo "$_command_result" | '{python_exe}' -c 'from bsm.shell import main;main(shell_name='sh',command='{command}')'
  fi
  unset _command_result

  return "$_{command}_bsm_exit_code"
}}

bsm_script() {{
  local _check_shell="$('{python_exe}' -c 'from bsm import main;main(check_shell=True)' "$*" 2>/dev/null)"

  if [ "$_check_shell" = 'BSM:OUTPUT_IS_SHELL' ]; then
    '{python_exe}' -c 'from bsm import main;main()' --shell sh "$*"
  else
    >&2 echo 'This command does not output shell script'
    return 2
  fi
}}
'''.format(command=command, python_exe=python_exe)

        return bsm_func

    def exit_script(self, command):
        bsm_exit = '''\
#unset _{command}_bsm_exit_code
unset -f {command}_script
unset -f {command}
'''.format(command=command)
        return bsm_exit
