from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.logger import get_logger
_logger = get_logger()


class Selector(object):
    def __init__(self, prop):
        self.__prop = prop

    def select(self, running, idle):
        param = {}

        for n in [
                'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
                'release_setting', 'release_package', 'category', 'category_priority']:
            param['prop_'+n] = self.__prop[n].data_copy()

        param['running'] = running
        param['idle'] = idle

        try:
            with Handler() as h:
                return h.run('select', param)
        except HandlerNotFoundError as e:
            _logger.debug(
                'Select handler not found, will randomly select one step')
            return [next(iter(idle))]
        except Exception as e:
            _logger.error('Select handler run error: %s', e)
            raise
