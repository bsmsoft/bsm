from bsm.config.common import Common

class Attribute(Common):
    def load_attribute(self, config_scenario):
        try:
            self.update(run_handler(config_scenario.version_path['handler_python_dir'], 'attribute'))
        except Exception as e:
            pass
