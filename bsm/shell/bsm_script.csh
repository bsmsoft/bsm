set _bsm_check_shell=`sh -c "'$_bsm_python_exe' -c 'from bsm import main;main(check_shell=True)' $_bsm_argv 2>/dev/null"`

if ("$_bsm_check_shell" == 'BSM:OUTPUT_IS_SHELL') then
  "$_bsm_python_exe" -c 'from bsm import main;main()' --shell csh $_bsm_argv
  set _bsm_exit=$status
else
  echo 'This command does not output shell script' | sh -c 'cat 1>&2'
  set _bsm_exit=2
endif

unset _bsm_check_shell
