from bsm.config.util import load_packages

from bsm.handler import Handler

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()

class PackagePath(CommonDict):
    def __init__(self, config):
        super(PackagePath, self).__init__()

        with Handler(config['release_path']['handler_python_dir']) as h:
            for package, value in load_packages(
                    h, config['category_priority'], config['package']).items():
                category, subdir, version = value
                pkg_cfg = config['package'].package_config(category, subdir, package, version)
                self[package] = pkg_cfg['config'].get('path', {}).copy()
