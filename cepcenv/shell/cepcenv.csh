set _cepcenv_check_shell=`sh -c "'$_cepcenv_python_exe' -c 'from cepcenv import main;main(check_shell=True)' $_cepcenv_argv 2>/dev/null"`

if ("$_cepcenv_check_shell" == 'CEPCENV:OUTPUT_IS_SHELL') then
  set _cepcenv_script=`"$_cepcenv_python_exe" -c 'from cepcenv import main;main()' --shell csh $_cepcenv_argv`
  set _cepcenv_exit=$status
  test $_cepcenv_exit = 0 && eval "$_cepcenv_script"
  unset _cepcenv_script
else
  "$_cepcenv_python_exe" -c 'from cepcenv import main;main()' $_cepcenv_argv
  set _cepcenv_exit=$status
endif

unset _cepcenv_check_shell
