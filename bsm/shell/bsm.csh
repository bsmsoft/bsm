set _bsm_var_check_shell=`sh -c "'$_bsm_var_python_exe' -c "\""from bsm.cli import main;main(cmd_name='$_bsm_var_cmd_name',app_root='$_bsm_var_app_root',output_shell='csh',check_cli=True)"\"" !* 2>/dev/null"`

if ("$_bsm_var_check_shell" != 'BSM:COMMAND_LINE_INTERFACE_OK') then
  "$_bsm_var_python_exe" -c "from bsm.cli import main;main(cmd_name='$_bsm_var_cmd_name',app_root='$_bsm_var_app_root',output_shell='csh')" !*
  set _bsm_var_command_exit_code=$status
else
  set _bsm_var_tmpfile=`mktemp`
  "$_bsm_var_python_exe" -c "from bsm.cli import main;main(cmd_name='$_bsm_var_cmd_name',app_root='$_bsm_var_app_root',output_shell='csh')" !* > $_bsm_var_tmpfile
  set _bsm_var_command_exit_code=$status
  if ($_bsm_var_command_exit_code == 0) then
    source $_bsm_var_tmpfile
  endif
  rm -f $_bsm_var_tmpfile
  unset _bsm_var_tmpfile
endif

unset _bsm_var_check_shell

unset _bsm_var_app_root
unset _bsm_var_cmd_name
unset _bsm_var_python_exe

eval "exit $_bsm_var_command_exit_code"
