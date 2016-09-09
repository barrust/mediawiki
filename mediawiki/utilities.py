'''
Utility functions
'''
import pickle
import sys
from os import path


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
