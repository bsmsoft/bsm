import os
import click

from cepcenv.install import Install
from cepcenv.package_manager import PackageManager

from cepcenv.config.config_release import ConfigRelease
from cepcenv.config.config_release import ConfigReleaseError

from cepcenv.util import expand_path
from cepcenv.util import safe_mkdir
from cepcenv.util import safe_rmdir
from cepcenv.util import call

from cepcenv.logger import get_logger
_logger = get_logger()

def _download_http(url, dst):
    pos = url.rfind('/')
    if pos == -1:
        raise Exception('Can not find file name from url: {0}'.format(url))
    fn = url[pos+1:]
    fntmp = fn + '.tmp'

    if os.path.isfile(os.path.join(dst, fn)):
        return fn

    cmd = ['curl', '-f', '-L', '-s', '-S', '-R', '-o', fntmp, url]
    ret, out, err = call(cmd, cwd=dst)
    if ret != 0:
        raise Exception('Download http Failed {0} "{1}": {2}'.format(ret, url, out))

    cmd = ['mv', fntmp, fn]
    ret, out, err = call(cmd, cwd=dst)
    if ret != 0:
        raise Exception('Rename Failed {0} "{1}": {2}'.format(ret, fn, out))

    return fn

def _download_svn(url, dst, pkg, version):
    name = '{0}-{1}'.format(pkg, version)
    fn = name + '.tar.gz'

    if os.path.isfile(os.path.join(dst, fn)) and not os.path.isdir(os.path.join(dst, name)):
        return fn

    cmd = ['svn', 'export', '--force', url, name]
    ret, out, err = call(cmd, cwd=dst)
    if ret != 0:
        raise Exception('Download svn Failed: {0}'.format(url))

    cmd = ['tar', '-czf', fn, name]
    ret, out, err = call(cmd, cwd=dst)
    if ret != 0:
        raise Exception('Tar svn repo Failed: {0}'.format(name))

    safe_rmdir(os.path.join(dst, name))

    return fn

class Pack(object):
    def execute(self, config, config_version, destination):
        release_version = config_version.get('version')

        try:
            config_release = ConfigRelease(config_version)
        except ConfigReleaseError:
            _logger.debug('Install release definition: {0}'.format(release_version))
            install = Install(config, config_version)
            config_release = install.config_release()

        self.__pkg_mgr = PackageManager(config_version, config_release)

        if not destination:
            destination = os.getcwd()
        destination = expand_path(destination)
        pack_dir = os.path.join(destination, 'pack_'+release_version)

        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            version = pkg_info.get('package', {}).get('version')
            if not version:
                continue

            download = pkg_info.get('install', {}).get('download')
            if not download:
                continue

            url = download.get('param', {}).get('url')
            if not url:
                continue
            url = url.format(version=version)

            pkg_dir = os.path.join(pack_dir, pkg, version)
            safe_mkdir(pkg_dir)

            _logger.info('Packing {0}...'.format(pkg))

            if download.get('handler') == 'http':
                pkg_file = _download_http(url, pkg_dir)
            elif download.get('handler') == 'svn':
                pkg_file = _download_svn(url, pkg_dir, pkg, version)

            with open(os.path.join(pkg_dir, 'md5sum.txt'), 'w') as f:
                call(['md5sum', pkg_file], cwd=pkg_dir, stdout=f)
            with open(os.path.join(pkg_dir, 'sha1sum.txt'), 'w') as f:
                call(['sha1sum', pkg_file], cwd=pkg_dir, stdout=f)
            with open(os.path.join(pkg_dir, 'url.txt'), 'w') as f:
                f.write(url+'\n')

            _logger.info('Package {0} packed'.format(pkg))

        _logger.info('All packages in version {0} packed in {1}'.format(release_version, pack_dir))
