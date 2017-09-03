from cepcenv.loader import load_common

def load_package(pkg_type):
    return load_common(pkg_type, 'cepcenv.soft')

def download(download_type, param):
    downloader = load_common(download_type, 'cepcenv.soft.downloader')(param)
    downloader.download()
