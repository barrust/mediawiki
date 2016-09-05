import pickle
from os import path


def capture_for_unittest(fn):
    """ capture_for_unittest decorator """
    def wrapper(*args, **kwargs):
        ''' define the actions '''
        file_path = path.abspath('./tests/mock_api_data.p')
        with open(file_path, 'rb') as f:
            mock_data = pickle.load(f)
        # build out parts of the dictionary
        if args[0].api_url not in mock_data:
            mock_data[args[0].api_url] = dict()
            mock_data[args[0].api_url]['query'] = dict()
            mock_data[args[0].api_url]['data'] = dict()

        new_params = tuple(sorted(args[1].items()))
        # print it before we add anything else in like action and format
        # print(args[0].api_url, tuple(sorted(new_params[0].items())), ": ")
        res = fn(*args, **kwargs)
        # print(res)
        mock_data[args[0].api_url]['query'][new_params] = res
        with open(file_path, 'wb') as f:
            pickle.dump(mock_data, f, -1)
        return res
    return wrapper
