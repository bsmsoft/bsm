import os

from bsm.const import HANDLER_MODULE_NAME

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ReleasePathError(Exception):
    pass


class ReleasePath(CommonDict):
    def __init__(self, config):
        super(ReleasePath, self).__init__()

        if not ('version' in config['scenario'] and config['scenario']['version']):
            raise ReleasePathError('"version" not specified in config scenario')

        self['main_dir'] = os.path.join(config['release_dir'], config['scenario']['version'])
        self['content_dir'] = os.path.join(self['main_dir'], 'content')
        self['config_dir'] = os.path.join(self['content_dir'], 'config')
        self['config_package_dir'] = os.path.join(self['config_dir'], 'package')
        self['handler_dir'] = os.path.join(self['content_dir'], 'handler')
        self['handler_python_dir'] = os.path.join(self['main_dir'], 'handler')
        self['handler_module_dir'] = os.path.join(self['main_dir'], 'handler', HANDLER_MODULE_NAME)
        self['status_dir'] = os.path.join(self['main_dir'], 'status')
        self['status_file'] = os.path.join(self['status_dir'], 'status.yml')
