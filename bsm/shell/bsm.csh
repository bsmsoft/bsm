set _bsm_var_check_shell=`sh -c "'$_bsm_python_exe' -c "\""from bsm.cli import main;main(cmd_name='$_bsm_cmd_name',app_root='$_bsm_app_root',output_shell='csh',check_cli=True)"\"" $_bsm_argv 2>/dev/null"`

if ("$_bsm_var_check_shell" != 'BSM:COMMAND_LINE_INTERFACE_OK') then
  "$_bsm_python_exe" -c "from bsm.cli import main;main(cmd_name='$_bsm_cmd_name',app_root='$_bsm_app_root',output_shell='csh',check_cli=True)" $_bsm_argv
else
  set _bsm_script=`"$_bsm_python_exe" -c "from bsm.cli import main;main(cmd_name='$_bsm_cmd_name',app_root='$_bsm_app_root',output_shell='csh')" $_bsm_argv`
  set _bsm_exit=$status
  test $_bsm_exit = 0 && eval "$_bsm_script"
  unset _bsm_script
endif

unset _bsm_var_check_shell
