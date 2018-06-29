import os
import click

from bsm import BSM_VERSION

from bsm.cmd.base import Base

class Version(Base):
    def execute(self):
        return self.__bsm.version()click.echo('bsm {0}'.format(BSM_VERSION))
