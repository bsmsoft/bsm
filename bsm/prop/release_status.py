from bsm.util import ensure_list
from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.prop.util import prop_from_file

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


def _current_essential_attribute(prop_release_setting, prop_attribute):
    attribute = {}

    essential_attribute = ensure_list(
        prop_release_setting.get('essential_attribute', []))

    for att in essential_attribute:
        if att in prop_attribute:
            attribute[att] = prop_attribute[att]

    return attribute


class ReleaseStatus(CommonDict):
    def __init__(self, prop):
        super(ReleaseStatus, self).__init__()

        all_release_status = prop_from_file(prop['release_path']['status_file'], list)
        current_attribute = _current_essential_attribute(
            prop['release_setting'], prop['attribute'])

        for status in all_release_status:
            if status.get('attribute', {}) == current_attribute:
                self.update(status)
                break

    def save_release_status(self, prop_release_path, prop_attribute, prop_release_setting):
        all_release_status = prop_from_file(prop_release_path['status_file'], list)
        current_attribute = _current_essential_attribute(
            prop_release_setting, prop_attribute)

        self['attribute'] = current_attribute

        index = -1
        for i, status in enumerate(all_release_status):
            if status.get('attribute', {}) == current_attribute:
                index = i
                break

        if index < 0:
            all_release_status.append(self.data_copy())
        else:
            all_release_status[index] = self.data_copy()

        safe_mkdir(prop_release_path['status_dir'])
        dump_config(all_release_status, prop_release_path['status_file'])
