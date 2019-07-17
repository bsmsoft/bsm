from bsm.prop.util import load_packages

from bsm.handler import Handler

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()

class PackagesPath(CommonDict):
    def __init__(self, prop_packages, prop):
        super(PackagesPath, self).__init__()

        with Handler(prop['release_path']['handler_python_dir']) as h:
            for package, value in load_packages(
                    h, prop['category_priority'], prop_packages).items():
                category, subdir, version = value
                pkg_props = prop_packages.package_props(category, subdir, package, version)
                self[package] = pkg_props['prop'].get('path', {}).copy()
