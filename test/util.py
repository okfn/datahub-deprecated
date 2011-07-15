from datahub import core
from datahub import web


FIXTURE_USER = {'name': 'fixture', 
                'full_name': 'Fixture',
                'email': 'fixture@datahub.net',
                'password': 'password',
                'password_confirm': 'password'}

AUTHZ = FIXTURE_USER['name'] + ':' + FIXTURE_USER['password']
AUTHZ = 'Basic ' + AUTHZ.encode('base64')

def create_fixture_user(app):
    app.post('/register', data=FIXTURE_USER)

def make_test_app():
    web.app.config['TESTING'] = True
    web.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    web.app.config['ELASTIC_SEARCH_INDEX'] = 'datahub_test'
    core.db.create_all()
    #manage.resetsearch()
    return web.app.test_client()

def tear_down_test_app():
    core.db.session.rollback()
    core.db.drop_all()

