import os
import click

from cepcenv.package_manager import PackageManager

from cepcenv.util import expand_path
from cepcenv.util import safe_mkdir
from cepcenv.util import safe_rmdir
from cepcenv.util import call

from cepcenv.logger import get_logger
_logger = get_logger()

def _download_http(url, dst, version):
    final_url = url.format(version=version)
    pos = final_url.rfind('/')
    if pos == -1:
        raise Exception('Can not find file name from url: {0}'.format(final_url))
    fn = final_url[pos+1:]

    if os.path.isfile(os.path.join(dst, fn)):
        return fn

    cmd = ['curl', '-f', '-L', '-s', '-S', '-R', '-O', final_url]
    ret, out, err = call(cmd, cwd=dst)
    if ret != 0:
        raise Exception('Download http Failed: {0}'.format(final_url))

    return fn

def _download_svn(url, dst, pkg, version):
    name = '{0}-{1}'.format(pkg, version)
    fn = name + '.tar.gz'

    if os.path.isfile(os.path.join(dst, fn)):
        return fn

    final_url = url.format(version=version)
    cmd = ['svn', 'export', '--force', final_url, name]
    ret, out, err = call(cmd, cwd=dst)
    if ret != 0:
        raise Exception('Download svn Failed: {0}'.format(final_url))

    cmd = ['tar', '-czf', fn, name]
    ret, out, err = call(cmd, cwd=dst)
    if ret != 0:
        raise Exception('Tar svn repo Failed: {0}'.format(name))

    safe_rmdir(os.path.join(dst, name))

    return fn

class Pack(object):
    def execute(self, config, config_version, config_release, destination):
        self.__pkg_mgr = PackageManager(config_version, config_release)

        if not destination:
            destination = os.getcwd()
        destination = expand_path(destination)

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

            pkg_dir = os.path.join(destination, pkg, version)
            safe_mkdir(pkg_dir)

            _logger.info('Packing {0}...'.format(pkg))

            if download.get('handler') == 'http':
                pkg_file = _download_http(download.get('param', {}).get('url', ''), pkg_dir, version)
            elif download.get('handler') == 'svn':
                pkg_file = _download_svn(download.get('param', {}).get('url', ''), pkg_dir, pkg, version)

            with open(os.path.join(pkg_dir, 'md5sum.txt'), 'w') as f:
                call(['md5sum', pkg_file], cwd=pkg_dir, stdout=f)
            with open(os.path.join(pkg_dir, 'sha1sum.txt'), 'w') as f:
                call(['sha1sum', pkg_file], cwd=pkg_dir, stdout=f)

            _logger.info('Package {0} packed'.format(pkg))
