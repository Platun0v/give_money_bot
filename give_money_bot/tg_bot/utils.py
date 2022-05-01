import hashlib


class CallbackData:
    def __init__(self) -> None:
        variables = self.__class__.__dict__.keys()
        for key in variables:
            if "__" not in key and isinstance(self.__getattribute__(key), str) and not self.__getattribute__(key):
                hash_value = hashlib.sha1(key.encode()).hexdigest()
                self.__setattr__(key, hash_value[:8])
