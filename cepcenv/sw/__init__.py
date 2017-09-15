import platform
import re

from cepcenv.util import check_output


def _detect_arch():
    return platform.machine()

def _detect_os():
    return 'sl6'

def _detect_compiler(compiler='gcc'):
    output = check_output(['gcc', '--version'])
    m = re.match('gcc \(GCC\) (\d+)\.(\d+)', output)
    version_major = m.group(1)
    version_minor = m.group(2)
    return 'gcc{0}{1}'.format(version_major, version_minor)


class Platform(object):
    def __init__(self, arch=None, os=None, compiler=None):
        self.__arch = (arch or _detect_arch())
        self.__os = (os or _detect_os())
        self.__compiler = (compiler or _detect_compiler())

    @property
    def arch(self):
        return self.__arch

    @property
    def os(self):
        return self.__os

    @property
    def compiler(self):
        return self.__compiler

    @property
    def platform(self):
        return '-'.join([self.__arch, self.__os, self.__compiler])
