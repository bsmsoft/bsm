import click

from pip import main

class Upgrade(object):
    def execute(self, config):
        main(['install', '--upgrade', 'pip'])
        main(['install', '--upgrade', 'cepcenv'])
