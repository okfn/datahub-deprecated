from datadeck.model import Resource

def list_by_user(user_name):
    # TODO: check if user actually exists.
    return Resource.query.filter_by(Resource.user.name==user_name)

def create():
    pass
