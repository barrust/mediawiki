''' random functions that will be needed for the tests '''


class FunctionUseCounter(object):
    ''' decorator to keep a running count of how many
    times function has been called; stop at 50 '''

    def __init__(self, func):
        ''' init decorator '''
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        ''' what to do when called '''
        self.count += 1
        if self.count > 50:  # arbitrary large
            return dict()
        return self.func(*args, **kwargs)


def find_depth(node):
    ''' find depth of tree '''
    def walk(next_node, depth):
        ''' walk down tree finding depth '''
        if next_node is None:
            return depth
        if 'sub-categories' not in next_node:
            return depth
        if next_node['sub-categories'] is None:
            return depth

        if len(next_node['sub-categories'].keys()) == 0:
            return next_node['depth']
        else:
            for key in next_node['sub-categories'].keys():
                path_depth = walk(next_node['sub-categories'][key], depth)
                if path_depth and path_depth > depth:
                    depth = path_depth
            return depth
    return walk(node, 0)
