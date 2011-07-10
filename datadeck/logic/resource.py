from datadeck.model import Resource, Account

def list_by_owner(owner_name):
    # TODO: check if user actually exists.
    return Resource.query.join(Resource.owner).filter(Account.name==owner_name)

def create():
    pass
