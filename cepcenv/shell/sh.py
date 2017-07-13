import sys

from cepcenv.shell.base import Base

class Sh(Base):
    def __init__(self):
        pass

    def set_env(self, env_name, env_value):
        return 'export %s="%s"\n' % (env_name, env_value)

    def source(self, script_path):
        return '. %s\n' % script_path

    def define_cepcenv(self):
        python_exe = sys.executable or 'python'

        cepcenv_func = '''
cepcenv() {
  command=$1

  case $command in
    use|setup|cleanup)
      script=$(%(python_exe)s -c 'from cepcenv.cmd import main;main()' $*)
      exit_code=$?
#      [ $exit_code -eq 0 ] && eval "$script"
      [ $exit_code -eq 0 ] && echo "script:\\n$script"
      ;;

    *)
      %(python_exe)s -c 'from cepcenv.cmd import main;main()' $*
      exit_code=$?
      ;;
  esac

  return "$exit_code"
}
''' % {'python_exe': python_exe}

        return cepcenv_func
