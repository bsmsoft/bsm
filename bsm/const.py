import os

BSM_HOME = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(BSM_HOME, 'VERSION'), 'r') as version_file:
    BSM_VERSION = version_file.read().strip()

with open(os.path.join(BSM_HOME, 'BSMCLI_CMD')) as bsmcli_cmd_file:
    BSMCLI_CMD = bsmcli_cmd_file.read().strip()


# This name is very long in order to avoid conflicts with other modules
HANDLER_MODULE_NAME = '_bsm_handler_run_avoid_conflict'
