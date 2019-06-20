from bsm.config.util import detect_category

from bsm.operation import Base

class DetectCategory(Base):
    def execute(self, directory):
        return detect_category(self._config['category'], directory)
