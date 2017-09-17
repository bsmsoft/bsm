cepcenv
=======

CEPC software management toolkit

Install cepcenv
---------------

Install ``cepcenv`` with ``curl`` or ``wget`` ::

    \curl -sSL https://raw.githubusercontent.com/xianghuzhao/cepcenv/master/tool/install.sh | sh -s [CEPCENV_INSTALL_DIR]

or ::

    \wget -qO- https://raw.githubusercontent.com/xianghuzhao/cepcenv/master/tool/install.sh | sh -s [CEPCENV_INSTALL_DIR]

If ``CEPCENV_INSTALL_DIR`` is omitted, ``cepcenv`` will be installed in the current directory.

Install cepcsoft with cepcenv
-----------------------------

Setup ``cepcenv``::

    source <CEPCENV_INSTALL_DIR>/setup.sh

Install specified ``cepcsoft`` version and where to install::

    cepcenv -r <CEPCSOFT_INSTALL_DIR> install <version>
