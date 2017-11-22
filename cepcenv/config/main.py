from cepcenv.util import expand_path

from cepcenv.config import load_config


def load_main(options_common):
    config = {}

    config_file = options_common.get('config_file')
    if config_file:
        try:
            c = load_config(expand_path(config_file))
            if not isinstance(c, dict):
                c = {}
            config.update(c)
        except:
            pass

    # The final verbose value: config['verbose'] || verbose
    if ('verbose' not in config) or (not config['verbose']):
        config['verbose'] = options_common.get('verbose', False)

    return config
