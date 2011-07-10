from datadeck.core import db
from datadeck.exc import NotFound
from datadeck.model import Resource, Account, User

from datadeck.logic import account

def list_by_owner(owner_name):
    # TODO: check if user actually exists.
    return Resource.query.join(Resource.owner).filter(Account.name==owner_name)

def get(owner_name, resource_name):
    """ Get will try to find a resource and return None if no resource is
    found. Use `find` for an exception-generating variant. """
    return Resource.query.join(Resource.owner).\
            filter(Account.name==owner_name).\
            filter(Resource.name==resource_name).first()

def find(owner_name, resource_name):
    """ Find a resource or yield a `NotFound` exception. """
    resource = get(owner_name, resource_name)
    if resource is None:
        raise NotFound('No such resource: %s / %s' % (owner_name, 
                       resource_name))
    return resource

def create(owner_name, data):
    # TODO: get a proper lookup
    owner = account.find(owner_name)

    # TODO: validation

    resource = Resource(owner, data['name'])
    db.session.add(resource)
    db.session.flush()

    return resource
