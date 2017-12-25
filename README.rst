cepcenv
=======

CEPC software management toolkit


Install cepcenv
---------------

Install ``cepcenv`` with ``curl`` or ``wget`` ::

    curl -sSL http://cepcsoft.ihep.ac.cn/package/cepcenv/script/install.sh | sh -s [CEPCENV_DIR]

or ::

    wget -qO- http://cepcsoft.ihep.ac.cn/package/cepcenv/script/install.sh | sh -s [CEPCENV_DIR]

If ``CEPCENV_DIR`` is omitted, ``cepcenv`` will be installed in the current directory.


Install cepcsoft with cepcenv
-----------------------------

``git`` command is necessary for executing the following commands. ``git`` could
be installed via the package manager::

    yum install -y git

Setup ``cepcenv``::

    . <CEPCENV_DIR>/setup.sh

List available ``cepc-release`` version::

    cepcenv ls-remote

Specified ``cepc-release`` version and where to install::

    cepcenv [-r <CEPCSOFT_INSTALL_DIR>] install <version>

If ``-r <CEPCSOFT_INSTALL_DIR>`` is not specified, everything will be installed
in the current directory.

List local installed ``cepc-release`` version::

    cepcenv -r <CEPCSOFT_INSTALL_DIR> ls

Select local ``cepc-release`` version you would like to use::

    cepcenv -r <CEPCSOFT_INSTALL_DIR> use <version>
