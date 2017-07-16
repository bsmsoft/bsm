import sys

from cepcenv.shell import Shell

class Sh(Shell):
    def set_env(self, env_name, env_value):
        return 'export %s="%s"\n' % (env_name, env_value)

    def source(self, script_path):
        return '. %s\n' % script_path

    def define_cepcenv(self):
        python_exe = sys.executable or 'python'

        cepcenv_func = '''
cepcenv() {
  check_shell=$(%(python_exe)s -c 'from cepcenv import main;main(check_shell=True)' $* 2>/dev/null)
  check_shell_exit_code=$?

  if [ $check_shell_exit_code = 0 -a "$check_shell" = 'CEPCENV:OUTPUT_IS_SHELL' ]; then
    script=$(%(python_exe)s -c 'from cepcenv import main;main()' --shell=sh $*)
    exit_code=$?
    [ $exit_code -eq 0 ] && eval "$script"
  else
    %(python_exe)s -c 'from cepcenv import main;main()' $*
    exit_code=$?
  fi

  return "$exit_code"
}

cepcenv_script() {
  check_shell=$(%(python_exe)s -c 'from cepcenv import main;main(check_shell=True)' $* 2>/dev/null)
  check_shell_exit_code=$?

  if [ $check_shell_exit_code = 0 -a "$check_shell" = 'CEPCENV:OUTPUT_IS_SHELL' ]; then
    %(python_exe)s -c 'from cepcenv import main;main()' --shell=sh $*
  else
    >&2 echo 'This command does not output shell script'
    return 2
  fi
}
''' % {'python_exe': python_exe}

        return cepcenv_func
