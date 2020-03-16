import os

from bsm.error import ConfigLoadError

from bsm.util.config import load_config

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ReleaseSettingOrigin(CommonDict):
    def __init__(self, prop_release_path):
        super(ReleaseSettingOrigin, self).__init__()

        config_dir = prop_release_path['config_dir']

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
        except ConfigLoadError as e:
            _logger.warning('Release setting file load error: %s', e)
            return

        self.update(release_setting)
