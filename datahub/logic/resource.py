from datahub.core import db
from datahub.exc import NotFound
from datahub.model import Resource, Account

from datahub.logic import account

def list_by_owner(owner_name):
    owner = account.find(owner_name)
    return Resource.query.join(Resource.owner).filter(Account.name==owner.name)

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
    owner = account.find(owner_name)

    # TODO: validation

    resource = Resource(owner, data['name'])
    db.session.add(resource)
    db.session.flush()

    return resource

def update(owner_name, resource_name, data):
    resource = find(owner_name, resource_name)

    resource.name = data['name']
    db.session.flush()

    return resource

def delete(owner_name, resource_name):
    resource = find(owner_name, resource_name)
    
    db.session.delete(resource)
    db.session.flush()

    
