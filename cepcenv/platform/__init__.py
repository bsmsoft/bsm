import platform
import re
import distro

from cepcenv.util import check_output


def _detect_arch():
    return platform.machine()

def _detect_os():
    id = distro.id()
    name = distro.name()
    major = distro.major_version()
    minor = distro.minor_version()
    if name.startswith('Scientific'):
        return 'sl'+major
    if name.startswith('Red Hat Enterprise'):
        return 'rhel'+major
    if id == 'centos':
        return 'centos'+major
    if id == 'debian':
        return 'debian'+major
    if id == 'arch':
        return 'arch'
    if id == 'gentoo':
        return 'gentoo'+major+'.'+minor
    if id == 'ubuntu':
        return 'ubuntu'+major+minor
    if id == 'fedora':
        return 'fedora'+major
    if name.startswith('openSUSE'):
        return 'opensuse'+major
    return 'unknown'

def _detect_compiler(compiler='gcc'):
    try:
        output = check_output(['gcc', '--version'])
        m = re.match('gcc \(GCC\) (\d+)\.(\d+)', output)
        version_major = m.group(1)
        version_minor = m.group(2)
        return 'gcc{0}{1}'.format(version_major, version_minor)
    except Exception as e:
        return 'unknown'


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
        return '-'.join([self.__arch, self.__os])
