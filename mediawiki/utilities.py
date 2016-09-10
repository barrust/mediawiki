'''
Utility functions
'''
import pickle
import sys
import functools
from os import path


# http://stackoverflow.com/a/8629441
class Memoize(object):
    ''' cache or memoize the data '''
    def __init__(self, func):
        ''' init the class here '''
        self.func = func
        self.name = func.__name__
        self._cache = None

    def __call__(self, *args, **kwargs):
        ''' define the __call__ method '''
        if self.name not in self._cache:
            self._cache[self.name] = dict()
        key = list()
        key.extend(args[1:])
        for k in kwargs.keys():
            key.append('({0}: {1})' .format(k, kwargs[k]))
        key = ' - '.join(key)
        if key in self._cache[self.name]:
            # print('get stored version')
            value = self._cache[self.name][key]
        else:
            # print('get it the first time')
            value = self.func(*args, **kwargs)
            self._cache[self.name][key] = value
        return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        # print "Get", obj, objtype
        func = functools.partial(self.__call__, obj)
        if not hasattr(obj, '_cache'):
            obj._cache = dict()
        self._cache = obj._cache
        return func


def capture_for_unittest(func):
    """ capture_for_unittest decorator """
    def wrapper(*args, **kwargs):
        ''' define the actions '''
        file_path = path.abspath('./tests/mock_api_data.p')
        with open(file_path, 'rb') as mock:
            mock_data = pickle.load(mock)
        # build out parts of the dictionary
        if args[0].api_url not in mock_data:
            mock_data[args[0].api_url] = dict()
            mock_data[args[0].api_url]['query'] = dict()
            mock_data[args[0].api_url]['data'] = dict()

        new_params = tuple(sorted(args[1].items()))
        res = func(*args, **kwargs)
        mock_data[args[0].api_url]['query'][new_params] = res
        with open(file_path, 'wb') as mock:
            pickle.dump(mock_data, mock, -1)
        return res
    return wrapper


def stdout(text, default='UTF8'):
    ''' Ensure that output to stdout is correctly handled '''
    encoding = sys.stdout.encoding or default
    if sys.version_info > (3, 0):
        return text.encode(encoding).decode(encoding)
    return text.encode(encoding)
