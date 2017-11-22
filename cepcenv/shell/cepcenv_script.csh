set _cepcenv_check_shell=`sh -c "'$_cepcenv_python_exe' -c 'from cepcenv import main;main(check_shell=True)' $_cepcenv_argv 2>/dev/null"`

if ("$_cepcenv_check_shell" == 'CEPCENV:OUTPUT_IS_SHELL') then
  "$_cepcenv_python_exe" -c 'from cepcenv import main;main()' --shell csh $_cepcenv_argv
  set _cepcenv_exit=$status
else
  echo 'This command does not output shell script' | sh -c 'cat 1>&2'
  set _cepcenv_exit=2
endif

unset _cepcenv_check_shell
