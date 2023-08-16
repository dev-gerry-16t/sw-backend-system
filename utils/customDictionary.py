
class CustomDictionary:
    def __init__(self, initial_value):
        self.data = initial_value

    def get(self, key, default_value=None):
        if self.data is not None:
            value = self.data.get(key)
            if value is not None:
                return value
            else:
                return default_value
        else:
            return default_value