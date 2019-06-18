from bsm.config.common import Common
from bsm.config.util import find_top_priority

from bsm.handler import Handler

from bsm.logger import get_logger
_logger = get_logger()

class PackagePath(Common):
    def __init__(self, config_release_path, config_category, config_package):
        super(PackagePath, self).__init__()

        category_priority = config_category['priority']

        packages = {}

        for category in category_priority:
            if category not in config_package:
                continue
            for subdir in config_package[category]:
                for package in config_package[category][subdir]:
                    for version, value in config_package[category][subdir][package].items():
                        packages.setdefault(package, [])
                        packages[package].append((category, subdir, version))

        with Handler(config_release_path['handler_python_dir']) as h:
            for pkg, value in packages.items():
                ctg, sd, ver = find_top_priority(h, category_priority, value)
                pkg_cfg = config_package.package_config(ctg, sd, pkg, ver)
                self[pkg] = pkg_cfg['config'].get('path', {}).copy()
