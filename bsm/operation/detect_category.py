import os

from bsm.util import expand_path

from bsm.operation import Base

class DetectCategory(Base):
    def execute(self, directory):
        dir_expand = expand_path(directory)

        root_found = None
        category_found = None
        for ctg, cfg in self._config['category']['content'].items():
            if 'root' in cfg and dir_expand.startswith(cfg['root']):
                # In case category is a subdir of another, select the deeper one
                if root_found is None or len(root_found) < len(cfg['root']):
                    root_found = cfg['root']
                    category_found = ctg

        if category_found is None:
            return None, None

        subdir = dir_expand[len(root_found):].strip(os.sep)
        return category_found, root_found
