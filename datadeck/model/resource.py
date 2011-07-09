from datadeck.core import db

def list_by_user(user_name):
    # TODO: check if user actually exists.
    return db.entity.find({'user': user_name})

def create():
    pass
