import os

from bsm.error import ConfigLoadError

from bsm.util import walk_rel_dir
from bsm.util.config import load_config

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ReleasePackageOrigin(CommonDict):
    def __init__(self, prop_release_path):
        super(ReleasePackageOrigin, self).__init__()

        for full_path, rel_dir, f in walk_rel_dir(prop_release_path['config_package_dir']):
            if not f.endswith('.yml') and not f.endswith('.yaml'):
                continue
            pkg_name = os.path.splitext(f)[0]
            try:
                self[os.path.join(rel_dir, pkg_name)] = load_config(full_path)
            except ConfigLoadError as e:
                _logger.warning('Fail to load package config file "%s": %s', full_path, e)
