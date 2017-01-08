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

        # print(next_node.keys())
        if len(next_node['sub-categories'].keys()) == 0:
            # print("got to the bottom...", next_node['depth'])
            # print('returning', next_node['depth'])
            return next_node['depth']
        else:
            # print(next_node)
            for key in next_node['sub-categories'].keys():
                path_depth = walk(next_node['sub-categories'][key], depth)
                # print('path_depth', path_depth)
                if path_depth and path_depth > depth:
                    depth = path_depth
            return depth
    return walk(node, 0)
