from functools import wraps


def singleton(cls):
    """Декоратор синглтона"""

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    return wrapper
