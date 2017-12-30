cepcenv
=======

CEPC software management toolkit


Install cepcenv
---------------

Install ``cepcenv`` with ``curl`` or ``wget`` ::

    curl -sSL http://cepcsoft.ihep.ac.cn/package/cepcenv/script/install.sh | sh -s [CEPCENV_DIR]

or ::

    wget -qO- http://cepcsoft.ihep.ac.cn/package/cepcenv/script/install.sh | sh -s [CEPCENV_DIR]

If ``CEPCENV_DIR`` is omitted, ``cepcenv`` will be installed in the
current directory.


Install cepcsoft with cepcenv
-----------------------------

Setup ``cepcenv``::

    . <CEPCENV_DIR>/setup.sh

List available CEPC software version::

    cepcenv ls-remote

Specify CEPC software version and where to install::

    cepcenv [-r <SOFTWARE_ROOT>] install <version>

If ``-r <SOFTWARE_ROOT>`` is not specified, everything will be
installed in the current directory.

Multiple versions could be installed under the same software root
directory.


Configuration
-------------

Create the configuration file if it does not exist::

    [ -e ~/.cepcenv.conf ] || cepcenv config -e > ~/.cepcenv.conf

Edit `~/.cepcenv.conf` and uncomment `software_root`::

    software_root: <SOFTWARE_ROOT>


Select cepcsoft Version
-----------------------

List local installed CEPC software version::

    cepcenv -r <SOFTWARE_ROOT> ls

Select local CEPC software version you would like to use::

    cepcenv -r <SOFTWARE_ROOT> use <version>
