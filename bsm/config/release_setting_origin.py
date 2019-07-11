import os

from bsm.util.config import load_config, ConfigError

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ConfigReleaseSettingOriginError(Exception):
    pass


class ReleaseSettingOrigin(CommonDict):
    def __init__(self, config_release_path):
        super(ReleaseSettingOrigin, self).__init__()

        config_dir = config_release_path['config_dir']

        config_file = None
        for setting_file in ['setting.yml', 'setting.yaml']:
            config_file = os.path.join(config_dir, setting_file)
            if os.path.isfile(config_file):
                break
        if config_file is None:
            _logger.warning('Release setting file "%s" not found')
            return

        try:
            release_setting = load_config(config_file)
        except ConfigError as e:
            _logger.warning('Release setting file load error: %s', e)
            return

        self.update(release_setting)
