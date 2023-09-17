# pylint: disable=redefined-outer-name
import functools
from datetime import datetime, timedelta


def cache(ttl=timedelta(minutes=1)):
    """
    https://stackoverflow.com/a/50866968/2966951
    """

    def wrap(func):
        cache = {}  # type: ignore

        @functools.wraps(func)
        def wrapped(*args, **kw):
            now = datetime.now()
            # see lru_cache for fancier alternatives
            key = tuple(args), frozenset(kw.items())
            if key not in cache or now - cache[key][0] > ttl:
                value = func(*args, **kw)
                cache[key] = (now, value)
            return cache[key][1]

        return wrapped

    return wrap
