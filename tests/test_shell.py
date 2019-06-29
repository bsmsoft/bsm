import subprocess

import pytest

from bsm.util import call, which

from bsm.shell import Shell


SPECIAL_STRINGS = [
        'simple',

        '',
        ' ',
        '\\',
        '\'',
        '\t',
        '!',

        'String with  space   ',
        '\nString with \nline break\n',
        'String with  empty \t  \n ',

        'String with special `~!@#$%^&*()-_=+[{]};:\'"\\|,<.>/?\n\t abc ABC 0123',
]


@pytest.fixture(params=['sh', 'csh'])
def shell(request):
    return Shell(request.param, 'test_bsm', '/fake_app_root')


def test_nonexsit(shell):
    with pytest.raises(AttributeError):
        shell.nonexsit_method()

def test_newline(shell):
    shell.newline(5)
    assert shell.script == '\n\n\n\n\n'
    shell.clear_script()
    assert not shell.script

def test_add_script(shell):
    shell.add_script('init')
    assert shell.script
    shell.clear_script()
    shell.add_script('exit')
    assert shell.script


def _get_available_shell_cmd():
    all_shell_cmd = []

    if which('sh'):
        all_shell_cmd.append(('sh', ['sh', '-s']))
    if which('dash'):
        all_shell_cmd.append(('sh', ['dash', '-s']))
    if which('bash'):
        all_shell_cmd.append(('sh', ['bash', '-s', '-O', 'expand_aliases']))
        all_shell_cmd.append(('sh', ['bash', '--posix', '-s']))
    if which('zsh'):
        all_shell_cmd.append(('sh', ['zsh', '-s']))

    if which('csh'):
        all_shell_cmd.append(('csh', ['csh', '-s']))
    if which('tcsh'):
        all_shell_cmd.append(('csh', ['tcsh', '-s']))

    return all_shell_cmd


@pytest.fixture(params=_get_available_shell_cmd())
def shell_with_cmd(request):
    return Shell(request.param[0], 'test_bsm', '/fake_app_root'), request.param[1]


def _execute_shell(cmd, script):
    ret, out, err = call(cmd, stderr=subprocess.PIPE, input=script.encode())
    return out.decode()


def test_comment(shell_with_cmd):
    shell, cmd = shell_with_cmd

    shell.comment('  This should not do anything\n  Including this line')
    assert '' == _execute_shell(cmd, shell.script)

def test_print(shell_with_cmd):
    shell, cmd = shell_with_cmd

    for s in SPECIAL_STRINGS:
        shell.clear_script()
        shell.print(s)
        assert (s + '\n') == _execute_shell(cmd, shell.script)

def test_env(shell_with_cmd):
    shell, cmd = shell_with_cmd

    env_name = '_BSM_TEST_ENV'

    for s in SPECIAL_STRINGS:
        # Just do not test variables with newline
        new_s = s.replace('\n', '')

        shell.clear_script()
        shell.set_env(env_name, new_s)
        shell.print_env(env_name)
        assert (new_s + '\n') == _execute_shell(cmd, shell.script)

    shell.clear_script()
    shell.set_env(env_name, 'Just a string')
    shell.unset_env(env_name)
    shell.print_env(env_name)
    assert '\n' == _execute_shell(cmd, shell.script)

def test_alias(shell_with_cmd):
    shell, cmd = shell_with_cmd

    alias_name = 'long_alias_to_test'
    output_string = 'this is the alias test string'

    shell.alias(alias_name, 'echo \'{0}\''.format(output_string))
    assert (output_string + '\n') == _execute_shell(cmd, shell.script + '\n' + alias_name + '\n')

    shell.clear_script()
    shell.alias(alias_name, 'Just a string')
    shell.unalias(alias_name)
    assert '' == _execute_shell(cmd, shell.script + '\n' + alias_name + '\n')
