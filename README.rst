BSM
===

Bundled software manager


Installation
------------

Install ``BSM`` with ``curl`` or ``wget`` ::

    curl -sSL https://raw.githubusercontent.com/bsmhep/bsm/master/script/install.sh | sh -s [BSM_DIR]

or ::

    wget -qO- https://raw.githubusercontent.com/bsmhep/bsm/master/script/install.sh | sh -s [BSM_DIR]

If ``BSM_DIR`` is omitted, ``BSM`` will be installed in the
current directory.


Install Software with BSM
-------------------------

Setup ``BSM``::

    . <BSM_DIR>/setup.sh

List available software version::

    bsm ls-remote

Specify software version and where to install::

    bsm [-r <SOFTWARE_ROOT>] install <version>

If ``-r <SOFTWARE_ROOT>`` is not specified, everything will be
installed in the current directory.

Multiple versions could be installed under the same software root
directory.


Configuration
-------------

Create the configuration file if it does not exist::

    [ -e ~/.bsm.conf ] || bsm config -e > ~/.bsm.conf

Edit `~/.bsm.conf` and uncomment `software_root`::

    software_root: <SOFTWARE_ROOT>


Select Software Version
-----------------------

List local installed software version::

    bsm -r <SOFTWARE_ROOT> ls

Select local software version you would like to use::

    bsm -r <SOFTWARE_ROOT> use <version>
