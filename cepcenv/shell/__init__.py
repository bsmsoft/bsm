from cepcenv.loader import load_class
from cepcenv.util   import snake_to_camel

def load_shell(shell_name):
    module_name = 'cepcenv.shell.' + shell_name
    class_name = snake_to_camel(shell_name)
    return load_class(module_name, class_name)
