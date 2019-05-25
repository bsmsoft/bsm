from bsm.config.common import Common

class Property(Common):
    def load_property(self, config_scenario):
        try:
            self.update(run_handler(config_scenario.version_path['handler_python_dir'], 'property'))
        except Exception as e:
            pass
