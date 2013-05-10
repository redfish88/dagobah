""" DAG implementation used in job classes """

from copy import copy

class DAG(object):
    """ Directed acyclic graph implementation. """

    def __init__(self):
        """ Construct a new DAG with no nodes or edges. """
        self.graph = {}


    def add_node(self, node_name):
        """ Add a node if it does not exist yet, or error out. """
        if node_name in self.graph:
            raise KeyError('node %s already exists' % node_name)
        self.graph[node_name] = set()


    def add_edge(self, ind_node, dep_node):
        """ Add an edge (dependency) between the specified nodes. """
        if ind_node not in self.graph or dep_node not in self.graph:
            raise KeyError('one or more nodes do not exist in graph')
        self.graph[ind_node].add(dep_node)


    def downstream(self, node):
        """ Returns a list of all nodes this node has edges towards. """
        if node not in self.graph:
            raise KeyError('node %s is not in graph' % node)
        return list(self.graph[node])


    def from_dict(self, graph_dict):
        """ Reset the graph and build it from the passed dictionary.

        The dictionary takes the form of {node_name: [directed edges]}
        """

        self.reset_graph()
        for new_node in graph_dict.iterkeys():
            self.add_node(new_node)
        for ind_node, dep_nodes in graph_dict.iteritems():
            if not isinstance(dep_nodes, list):
                raise TypeError('dict values must be lists')
            for dep_node in dep_nodes:
                self.add_edge(ind_node, dep_node)


    def reset_graph(self):
        """ Restore the graph to an empty state. """
        self.graph = {}


    def ind_nodes(self):
        """ Returns a list of all nodes in the graph with no dependencies. """
        all_nodes, dependent_nodes = set(self.graph.keys()), set()
        for downstream_nodes in self.graph.itervalues():
            [dependent_nodes.add(node) for node in downstream_nodes]
        return list(all_nodes - dependent_nodes)


    def validate(self):
        """ Returns (Boolean, message) of whether DAG is valid. """
        if len(self.ind_nodes()) == 0:
            return (False, 'no independent nodes detected')
        try:
            self._topological_sort()
        except ValueError:
            return (False, 'failed topological sort')
        return (True, 'valid')


    def _dependencies(self, target_node, graph=None):
        """ Returns a list of all nodes from incoming edges. """

        if graph is None:
            graph = self.graph

        result = set()
        for node, outgoing_nodes in graph.iteritems():
            if target_node in outgoing_nodes:
                result.add(node)
        return list(result)


    def _topological_sort(self):
        """ Returns a topological ordering of the DAG.

        Raises an error if this is not possible (graph is not valid).
        """

        # woooo pseudocode from wikipedia!
        graph = copy(self.graph)
        l = []
        q = self.ind_nodes()
        while len(q) != 0:
            n = q.pop()
            l.append(n)
            iter_nodes = copy(graph[n])
            for m in iter_nodes:
                graph[n].remove(m)
                if len(self._dependencies(m)) == 0:
                    q.append(m)

        if len(l) != len(graph.keys()):
            raise ValueError('graph is not acyclic')
        return l
