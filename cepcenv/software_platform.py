import platform
import re

from cepcenv.util import call


def _detect_arch():
    return platform.machine()

def _detect_os():
    return 'sl6'

def _detect_compiler(compiler='gcc'):
    output = call(['gcc', '--version'])
    m = re.match('gcc \(GCC\) (\d+)\.(\d+)', output)
    version_major = m.group(1)
    version_minor = m.group(2)
    return 'gcc%s%s' % (version_major, version_minor)


class SoftwarePlatform(object):
    def __init__(self, config):
        self.__config = config

    def arch(self):
        if 'arch' in self.__config:
            return self.__config['arch']
        return _detect_arch()

    def os(self):
        if 'os' in self.__config:
            return self.__config['os']
        return _detect_os()

    def compiler(self):
        if 'compiler' in self.__config:
            return self.__config['compiler']
        return _detect_compiler()

    def all(self):
        return '-'.join([self.arch(), self.os(), self.compiler()])
