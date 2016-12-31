'''
Utility functions
'''
import sys
import json
import functools
import os
import inspect


def parse_all_arguments(func):
    ''' determine all positional and named arguments as a dict '''
    args = dict()
    if sys.version_info < (3, 0):
        func_args = inspect.getargspec(func)
        if func_args.defaults is not None:
            val = len(func_args.defaults)
        else:
            val = 0
        if func_args.defaults is not None:
            for i, itm in enumerate(func_args.args[1:-val]):
                args[itm] = func_args.defaults[i]
        for param in func_args.args[1:len(func_args.args) - val]:
            args[param] = None
    else:
        func_args = inspect.signature(func)
        for itm in list(func_args.parameters)[1:]:
            param = func_args.parameters[itm]
            if param.default is param.empty:
                args[param.name] = None
            else:
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
        tmp = list()
        tmp.extend(args[1:])
        for k in sorted(kwargs.keys()):
            tmp.append('({0}: {1})' .format(k, kwargs[k]))
        key = ' - '.join(tmp)

        # pull from the cache if it is available
        if key not in cache[func.__name__]:
            cache[func.__name__][key] = func(*args, **kwargs)
        return cache[func.__name__][key]
    return wrapper


def capture_response(func):
    ''' capture_response decorator to be used for tests '''
    def wrapper(*args, **kwargs):
        ''' define the actions '''
        file_path = os.path.abspath('./tests/mock_requests.json')
        if os.path.isfile(file_path):
            with open(file_path, 'r') as mock:
                mock_data = json.load(mock)
        else:
            mock_data = dict()

        new_params = json.dumps(tuple(sorted(args[1].items())))
        # build out parts of the dictionary
        if args[0].api_url not in mock_data:
            mock_data[args[0].api_url] = dict()
        try:
            res = func(*args, **kwargs)
        except Exception:
            res = dict()
        mock_data[args[0].api_url][new_params] = res
        with open(file_path, 'w') as mock:
            json.dump(mock_data, mock, ensure_ascii=False, indent=1,
                      sort_keys=True)
        return res
    return wrapper
