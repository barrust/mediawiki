'''
Utility functions
'''
import json
import functools
import os


def memoize(func):
    ''' quick memoize decorator for class instance methods '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ''' wrap it up and store info in a cache '''
        # add it to the class if needed
        if not hasattr(args[0], '_cache'):
            args[0]._cache = dict()
        cache = args[0]._cache
        if func.__name__ not in cache:
            cache[func.__name__] = dict()
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
