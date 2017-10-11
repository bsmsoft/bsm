import click

from pip import main

class Upgrade(object):
    def execute(self, config):
        def pip_install(package):
            main(['install', '--quiet', '--quiet', '--quiet', '--upgrade', package])

        pip_install('pip')
        pip_install('cepcenv')
