import os

from bsm.const import HANDLER_MODULE_NAME

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ReleasePathError(Exception):
    pass


class ReleasePath(CommonDict):
    def __init__(self, config_scenario, release_work_dir):
        super(ReleasePath, self).__init__()

        if 'software_root' not in config_scenario:
            raise ReleasePathError('"software_root" not specified in config scenario')

        self['release_dir'] = os.path.join(config_scenario['software_root'], release_work_dir)

        if not ('version' in config_scenario and config_scenario['version']):
            _logger.debug('"version" not specified in config scenario')
            return

        self['main_dir'] = os.path.join(self['release_dir'], config_scenario['version'])
        self['content_dir'] = os.path.join(self['main_dir'], 'content')
        self['config_dir'] = os.path.join(self['content_dir'], 'config')
        self['handler_dir'] = os.path.join(self['content_dir'], 'handler')
        self['handler_python_dir'] = os.path.join(self['main_dir'], 'handler')
        self['handler_module_dir'] = os.path.join(self['main_dir'], 'handler', HANDLER_MODULE_NAME)
        self['status_dir'] = os.path.join(self['main_dir'], 'status')
        self['status_file'] = os.path.join(self['status_dir'], 'status.yml')
