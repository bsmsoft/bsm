from cepcenv.soft import load_package

class Package(object):
    def __init__(self, pkg_type, param):
        self.__package_root = ''

        self.__pkg = load_package(pkg_type, param)

    def download(self):
        self.__pkg.download()

    def extract(self):
        self.__pkg.extract()
