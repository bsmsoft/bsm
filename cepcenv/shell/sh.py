import sys

from cepcenv.shell import Shell

class Sh(Shell):
    def set_env(self, env_name, env_value):
        return 'export {0}="{1}"\n'.format(env_name, env_value)

    def unset_env(self, env_name):
        return 'unset {0}\n'.format(env_name)

    def unset_func(self, func_name):
        return 'unset -f {0}\n'.format(func_name)

    def source(self, script_path):
        return '. {0}\n'.format(script_path)

    def define_cepcenv(self):
        python_exe = sys.executable or 'python'

        cepcenv_func = '''
cepcenv() {{
  check_shell=$({python_exe} -c 'from cepcenv import main;main(check_shell=True)' $* 2>/dev/null)
  check_shell_exit_code=$?

  if [ $check_shell_exit_code = 0 -a "$check_shell" = 'CEPCENV:OUTPUT_IS_SHELL' ]; then
    script=$({python_exe} -c 'from cepcenv import main;main()' --shell=sh $*)
    exit_code=$?
    [ $exit_code -eq 0 ] && eval "$script"
  else
    {python_exe} -c 'from cepcenv import main;main()' $*
    exit_code=$?
  fi

  return "$exit_code"
}}

cepcenv_script() {{
  check_shell=$({python_exe} -c 'from cepcenv import main;main(check_shell=True)' $* 2>/dev/null)
  check_shell_exit_code=$?

  if [ $check_shell_exit_code = 0 -a "$check_shell" = 'CEPCENV:OUTPUT_IS_SHELL' ]; then
    {python_exe} -c 'from cepcenv import main;main()' --shell=sh $*
  else
    >&2 echo 'This command does not output shell script'
    return 2
  fi
}}
'''.format(python_exe=python_exe)

        return cepcenv_func

    def undefine_cepcenv(self):
        return self.unset_func('cepcenv') + self.unset_func('cepcenv_script')
