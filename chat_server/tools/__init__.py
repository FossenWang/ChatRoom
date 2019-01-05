import functools
from asgiref.sync import async_to_sync


def async_to_sync_function(function):
    @functools.wraps(function)
    def sync_function(*args, **kwargs):
        return async_to_sync(function)(*args, **kwargs)
    return sync_function
