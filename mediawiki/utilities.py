'''
Utility functions
'''
import pickle
import sys
import functools
from os import path
import inspect


# http://stackoverflow.com/a/8629441
class Memoize(object):
    ''' cache or memoize the data '''
    def __init__(self, func):
        ''' init the class here '''
        self.func = func
        self.name = func.__name__
        self._cache = None
        self._default_params = dict()

        # inspect the function for parameters and default values
        fun_insp = inspect.getargspec(func)
        args = fun_insp[0]
        defaults = fun_insp[3]
        if defaults:
            have_defaults = args[-len(defaults):]
        else:
            have_defaults = list()
        # builld out the default parameters dictionary
        for i, item in enumerate(have_defaults):
            self._default_params[item] = defaults[i]
        # print(self._default_params)

    def __call__(self, *args, **kwargs):
        ''' define the __call__ method '''
        if self.name not in self._cache:
            self._cache[self.name] = dict()
        # ensure that we always have all parameters in the key
        all_params = kwargs.copy()
        for item in self._default_params:
            if item not in all_params:
                all_params[item] = self._default_params[item]
        # build the full key
        key = list()
        key.extend(args[1:])
        for k in sorted(all_params.keys()):
            key.append('({0}: {1})' .format(k, all_params[k]))
        key = ' - '.join(key)

        # do the caching
        if key in self._cache[self.name]:
            # print('get stored version')
            value = self._cache[self.name][key]
        else:
            # print('get it the first time')
            self._cache[self.name][key] = value = self.func(*args, **kwargs)
        return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        # print "Get", obj, objtype
        func = functools.partial(self.__call__, obj)
        if not hasattr(obj, 'cache'):
            obj.cache = dict()
        self._cache = obj.cache
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
