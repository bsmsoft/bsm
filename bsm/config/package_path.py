import os

from bsm.config.common import Common

from bsm.logger import get_logger
_logger = get_logger()


class _PackagePath(Common):
    def __init__(self, category):
        self.__category = category
        return super(_PackagePath, self).__init__()

    def __getitem__(self, key):
        if key not in self:
            value = {}
            value[
            super(_PackagePath, self).__setitem(key, value)

        return super(_PackagePath, self).__getitem__(key)

class PackagePath(Common):
    def load(self, config_category):
        for ctg, ctg_cfg in config_category.items():
            if 'config_package_dir' not in ctg_cfg:
                continue

            self[ctg] = _PackagePath(ctg)
