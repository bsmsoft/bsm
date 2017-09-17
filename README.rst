cepcenv
=======

CEPC software management toolkit

Install cepcenv
---------------

Install ``cepcenv`` with ``curl`` or ``wget`` ::

    \curl -sSL https://github.com/xianghuzhao/cepcenv/raw/master/tool/install.sh | sh -s [CEPCENV_DIR]

or ::

    \wget -qO- https://github.com/xianghuzhao/cepcenv/raw/master/tool/install.sh | sh -s [CEPCENV_DIR]

If ``CEPCENV_DIR`` is omitted, ``cepcenv`` will be installed in the current directory.

Install cepcsoft with cepcenv
-----------------------------

Setup ``cepcenv``::

    . <CEPCENV_DIR>/setup.sh

Specified ``cepcsoft`` version and where to install::

    cepcenv -r <CEPCSOFT_INSTALL_DIR> install <version>
