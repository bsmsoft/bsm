from bsm.operation import Base

class Check(Base):
    def execute(self, check_type):
        param = {}
        param['check_type'] = check_type
        param['config_release'] = self._config['release'].data_copy()

        try:
            return run_handler('checker', param, self._config['release_path']['handler_dir'])
        except LoadError as e:
            _logger.debug('Checker load failed: {0}'.format(e))
        except Exception as e:
            _logger.error('Checker run error: {0}'.format(e))
            raise

        return {}
