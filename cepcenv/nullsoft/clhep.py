class Clhep(object):
    def __init__(self, param, version):
        self.__param = param
        self.__version = version

        self.__url = 'https://proj-clhep.web.cern.ch/proj-clhep/DISTRIBUTION/tarFiles/clhep-{0}.tgz'.format(version)

    @property
    def downloader(self):
        p = {}
        p['type'] = 'http'
        p['param'] = {}
        p['param']['url'] = self.__url
        return p

    @property
    def extractor(self):
        return {'type': 'tar'}

    @property
    def compiler(self):
        return {'type': 'cmake'}
