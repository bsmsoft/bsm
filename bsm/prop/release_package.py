from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class ReleasePackage(CommonDict):
    def __init__(self, config):
        super(ReleasePackage, self).__init__()

        param = {}
        for name in [
                'app', 'output', 'scenario', 'option_release', 'release_path',
                'release_setting_origin', 'release_package_origin', 'attribute']:
            param['config_'+name] = config[name].data_copy()

        try:
            with Handler(config['release_path']['handler_python_dir']) as h:
                result = h.run('transform.release_package', param)
                if isinstance(result, dict):
                    self.update(result)
        except HandlerNotFoundError as e:
            _logger.debug('Transformer for release_package not found: %s', e)
            self.update(config['release_package_origin'])
        except Exception as e:
            _logger.error('Transformer for release_package run error: %s', e)
            raise
