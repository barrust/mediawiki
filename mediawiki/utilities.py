'''
Utility functions
'''
import sys
import functools
import inspect


def parse_all_arguments(func):
    ''' determine all positional and named arguments as a dict '''
    args = dict()
    if sys.version_info < (3, 0):
        func_args = inspect.getargspec(func)
        if func_args.defaults is not None:
            val = len(func_args.defaults)
            for i, itm in enumerate(func_args.args[-val:]):
                args[itm] = func_args.defaults[i]
    else:
        func_args = inspect.signature(func)
        for itm in list(func_args.parameters)[1:]:
            param = func_args.parameters[itm]
            if param.default is not param.empty:
                args[param.name] = param.default
    return args


def memoize(func):
    ''' quick memoize decorator for class instance methods '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ''' wrap it up and store info in a cache '''
        cache = args[0].memoized
        if func.__name__ not in cache:
            cache[func.__name__] = dict()
            if 'defaults' not in cache:
                cache['defaults'] = dict()
            cache['defaults'][func.__name__] = parse_all_arguments(func)
        # build a key; should also consist of the default values
        defaults = cache['defaults'][func.__name__].copy()
        for key, val in kwargs.items():
            defaults[key] = val
        tmp = list()
        tmp.extend(args[1:])
        for k in sorted(defaults.keys()):
            tmp.append('({0}: {1})' .format(k, defaults[k]))
        key = ' - '.join(tmp)

        # pull from the cache if it is available
        if key not in cache[func.__name__]:
            cache[func.__name__][key] = func(*args, **kwargs)
        return cache[func.__name__][key]
    return wrapper


def str_or_unicode(text):
    ''' handle python 3 unicode and python 2.7 byte strings '''
    encoding = sys.stdout.encoding
    if sys.version_info > (3, 0):
        return text.encode(encoding).decode(encoding)
    return text.encode(encoding)
