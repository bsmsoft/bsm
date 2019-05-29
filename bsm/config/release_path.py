import os

from bsm.const import HANDLER_MODULE_NAME

from bsm.config.common import Common

from bsm.logger import get_logger
_logger = get_logger()


class ReleasePath(Common):
    def load(self, config_scenario, config_app):
        if 'software_root' not in config_scenario:
            _logger.warn('"software_root" not specified')
            return

        self['release_dir'] = os.path.join(config_scenario['software_root'], config_app['release_work_dir'])

        if not ('version' in config_scenario and config_scenario['version']):
            _logger.warn('"version" not specified')
            return

        self['main_dir'] = os.path.join(self['release_dir'], config_scenario['version'])
        self['def_dir'] = os.path.join(self['main_dir'], 'def')
        self['config_dir'] = os.path.join(self['def_dir'], 'config')
        self['handler_dir'] = os.path.join(self['def_dir'], 'handler')
        self['handler_python_dir'] = os.path.join(self['main_dir'], 'handler')
        self['handler_module_dir'] = os.path.join(self['main_dir'], 'handler', HANDLER_MODULE_NAME)
        self['status_dir'] = os.path.join(self['main_dir'], 'status')
        self['install_status_file'] = os.path.join(self['status_dir'], 'install.yml')
