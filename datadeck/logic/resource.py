from datadeck.core import db
from datadeck.model import Resource, Account, User

def list_by_owner(owner_name):
    # TODO: check if user actually exists.
    return Resource.query.join(Resource.owner).filter(Account.name==owner_name)

def get(owner_name, resource_name):
    return Resource.query.join(Resource.owner).\
            filter(Account.name==owner_name).\
            filter(Resource.name==resource_name).first()

def create(owner_name, data):
    # TODO: get a proper lookup
    owner = User(owner_name)
    
    # TODO: validation

    resource = Resource(owner, data['name'])
    db.session.add(resource)
    db.session.flush()

    return resource
