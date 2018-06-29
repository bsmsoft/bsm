class Plain(object):
    def dump(self, value):
        if isinstance(value, list):
            return '\n'.join([str(v) for v in value])
        if isinstance(value, dict):
            return '\n'.join([str(k)+': '+str(v) for k, v in value.items()])
        return str(value)
