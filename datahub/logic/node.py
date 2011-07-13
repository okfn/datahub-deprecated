from datahub.model import Node

from datahub.logic.search import index_add

def rebuild():
    """ Rebuild the search index for all nodes. """
    for node in Node.query:
        index_add(node)
