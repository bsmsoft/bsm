import json

class Json(object):
    def dump(self, value):
        return json.dumps(value)
