import click

from pip import main

class Upgrade(object):
    def execute(self, config):
        arguments = ['install', '--upgrade', 'cepcenv']
        main(arguments)
