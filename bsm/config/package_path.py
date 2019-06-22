from bsm.config.util import load_packages

from bsm.handler import Handler

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()

class PackagePath(CommonDict):
    def __init__(self, config_release_path, config_category_priority, config_package):
        super(PackagePath, self).__init__()

        with Handler(config_release_path['handler_python_dir']) as h:
            for package, value in load_packages(h, config_category_priority, config_package).items():
                category, subdir, version = value
                pkg_cfg = config_package.package_config(category, subdir, package, version)
                self[package] = pkg_cfg['config'].get('path', {}).copy()
