CEPCENV_PATH="$( cd "$( dirname "$_" )" && pwd )"
export CEPCENV_PATH

read -r CEPCENV_VERSION < "$CEPCENV_PATH/VERSION"
export CEPCENV_VERSION

_cepcenv_python_run()
{
    PYTHONPATH=$CEPCENV_PATH/core:$PYTHONPATH python $CEPCENV_PATH/script/run.py $*
}

cepcenv()
{
    command=$1
    shift

    case $command in
        'version' )
            echo "cepcenv $CEPCENV_VERSION"
            ;;

        'install' )
            _cepcenv_python_run $command $*
            ;;

        'use' )
            newpath=$(_cepcenv_python_run $command $*)
            echo $?
            echo $newpath
            ;;

        * )
            >&2 echo 'No such command'
            ;;
    esac
}
