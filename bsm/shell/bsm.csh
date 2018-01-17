set _bsm_check_shell=`sh -c "'$_bsm_python_exe' -c 'from bsm import main;main(check_shell=True)' $_bsm_argv 2>/dev/null"`

if ("$_bsm_check_shell" == 'BSM:OUTPUT_IS_SHELL') then
  set _bsm_script=`"$_bsm_python_exe" -c 'from bsm import main;main()' --shell csh $_bsm_argv`
  set _bsm_exit=$status
  test $_bsm_exit = 0 && eval "$_bsm_script"
  unset _bsm_script
else
  "$_bsm_python_exe" -c 'from bsm import main;main()' $_bsm_argv
  set _bsm_exit=$status
endif

unset _bsm_check_shell
