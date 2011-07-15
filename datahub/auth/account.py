from datahub.core import current_user

from datahub.auth.util import logged_in

def read(account):
    return True

def update(account):
    return logged_in() and account == current_user

def create():
    return not logged_in()

