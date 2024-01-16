"""
Utility functions
"""
import functools
import inspect
import sys
import time
from typing import Any, Callable, Dict, Optional


def parse_all_arguments(func: Callable) -> Dict[str, Any]:
    """determine all positional and named arguments as a dict"""
    args = {}

    func_args = inspect.signature(func)
    for itm in list(func_args.parameters)[1:]:
        param = func_args.parameters[itm]
        if param.default is not param.empty:
            args[param.name] = param.default
    return args


def memoize(func: Callable) -> Callable:
    """quick memoize decorator for class instance methods
    NOTE: this assumes that the class that the functions to be
    memoized already has a memoized and refresh_interval
    property"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """wrap it up and store info in a cache"""
        cache = args[0].memoized
        refresh = args[0]._config.refresh_interval
        use_cache = args[0]._config.use_cache

        # short circuit if not using cache
        if use_cache is False:
            return func(*args, **kwargs)

        if func.__name__ not in cache:
            cache[func.__name__] = {}
            if "defaults" not in cache:
                cache["defaults"] = {}
            cache["defaults"][func.__name__] = parse_all_arguments(func)
        # build a key; should also consist of the default values
        defaults = cache["defaults"][func.__name__].copy()
        for key, val in kwargs.items():
            defaults[key] = val
        tmp = []
        tmp.extend(args[1:])
        for k in sorted(defaults.keys()):
            tmp.append(f"({k}: {defaults[k]})")

        tmp = [str(x) for x in tmp]
        key = " - ".join(tmp)

        # set the value in the cache if missing or needs to be refreshed
        if key not in cache[func.__name__]:
            cache[func.__name__][key] = (time.time(), func(*args, **kwargs))
        else:
            tmp = cache[func.__name__][key]
            # determine if we need to refresh the data...
            if refresh is not None and time.time() - tmp[0] > refresh:
                cache[func.__name__][key] = (time.time(), func(*args, **kwargs))
        return cache[func.__name__][key][1]

    return wrapper


def str_or_unicode(text: str) -> str:
    """handle python 3 unicode"""
    encoding = sys.stdout.encoding
    return text.encode(encoding).decode(encoding)


def is_relative_url(url: str) -> Optional[bool]:
    """simple method to determine if a url is relative or absolute"""
    return url.find("://") <= 0 and not url.startswith("//") if not url.startswith("#") else None
