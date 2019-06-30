import sys

from bsm.const import BSMCLI_BIN

from bsm.shell.base import Base

def _convert_sh_string(s):
    res = '\''
    for i in s:
        # "\" will be converted into four chars "'\\'"
        if i == '\\':
            res += '\'\\\\\''
        # "'" will be converted into four chars "'\''"
        elif i == '\'':
            res += '\'\\\'\''
        else:
            res += i
    res += '\''
    return res

class Sh(Base):
    def comment(self, content):
        lines = content.split('\n')
        newlines = ['# ' + l for l in lines]
        return '\n'.join(newlines) + '\n'

    def output(self, content):
        lines = content.split('\n')
        newlines = ['echo ' + _convert_sh_string(l) for l in lines]
        return '\n'.join(newlines) + '\n'

    def output_env(self, env_name):
        return 'echo "${0}"'.format(env_name)

    def set_env(self, env_name, env_value):
        return 'export {0}={1}\n'.format(env_name, _convert_sh_string(env_value))

    def unset_env(self, env_name):
        return 'unset {0}\n'.format(env_name)

    def alias(self, alias_name, alias_value):
        return 'alias {0}={1}\n'.format(alias_name, _convert_sh_string(alias_value))

    def unalias(self, alias_name):
        return 'unalias {0} 2>/dev/null\n'.format(alias_name)

    def source(self, script_path):
        return '. \'{0}\'\n'.format(script_path)

    def script_init(self):
        python_exe = sys.executable or 'python'

        bsm_func = '''\
{cmd_name}() {{
  _bsm_var_check_cli="$('{python_exe}' -c "from bsm.cli import main;main(cmd_name='{cmd_name}',app_root='{app_root}',output_shell='sh',check_cli=True)" $* 2>/dev/null)"
  if [ "$_bsm_var_check_cli" != 'BSM:COMMAND_LINE_INTERFACE_OK' ]; then
    unset _bsm_var_check_cli
    '{python_exe}' -c "from bsm.cli import main;main(cmd_name='{cmd_name}',app_root='{app_root}',output_shell='sh')" $*
    return
  fi
  unset _bsm_var_check_cli

  _cmd_result=$('{python_exe}' -c "from bsm.cli import main;main(cmd_name='{cmd_name}',app_root='{app_root}',output_shell='sh')" $*)
  _bsm_var_command_exit_code=$?
  if [ "$_bsm_var_command_exit_code" -eq 0 ]; then
    eval "$_cmd_result"
    _bsm_var_command_exit_code=$?
  fi
  unset _cmd_result
  return $_bsm_var_command_exit_code
}}
'''.format(cmd_name=self._cmd_name, python_exe=python_exe, app_root=self._app_root)

        return bsm_func

    def script_exit(self):
        bsm_exit = '''\
unset -f {cmd_name} 2>/dev/null
'''.format(cmd_name=self._cmd_name)
        return bsm_exit

    def setup_script(self):
        script = '''\
eval "$('{bsmcli_bin}' --app-root '{app_root}' --shell sh init)"
'''.format(bsmcli_bin=BSMCLI_BIN, app_root=self._app_root)
        return script
