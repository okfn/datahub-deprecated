import unittest
import json

from datahub import core
from datahub import model
from datahub import web

JSON = 'application/json'


class ProfileTestCase(unittest.TestCase):

    def setUp(self):
        web.app.config['TESTING'] = True
        web.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        core.db.create_all()
        self.app = web.app.test_client()
        self.make_fixtures()

    def tearDown(self):
        core.db.drop_all()

    def make_fixtures(self):
        # TODO: call logic layer instead, once there is one:
        user = model.User('fixturix', 'Mr. Fixture', 'fix@ture.org',
                          'secret')
        core.db.session.add(user)
        core.db.session.commit()

    def test_account_profile_get(self):
        res = self.app.get('/api/v1/profile/no-such-user')
        assert res.status.startswith("404"), res.status
        res = self.app.get('/api/v1/profile/fixturix', 
                headers={'Accept': JSON})
        assert res.status.startswith("200"), res.status
        body = json.loads(res.data)
        assert body['name']=='fixturix', body

    def test_account_profile_put(self):
        res = self.app.get('/api/v1/profile/fixturix', 
                headers={'Accept': JSON})
        body = json.loads(res.data)
        body['name']='fixturix-renamed'
        res = self.app.put('/api/v1/profile/fixturix', 
                data=body, headers={'Accept': JSON})
        body = json.loads(res.data)
        assert body['name']=='fixturix-renamed', body

    def test_account_profile_put_invalid_name(self):
        body = {'name': 'fixturix renamed invalid'}
        res = self.app.put('/api/v1/profile/fixturix', 
                data=body, headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        body = json.loads(res.data)
        assert 'name' in body['errors'], body

    def test_account_profile_put_invalid_email(self):
        body = {'name': 'fixturix', 'email': 'bar', 'full_name': 'la la'}
        res = self.app.put('/api/v1/profile/fixturix', 
                data=body, headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        body = json.loads(res.data)
        assert 'email' in body['errors'], body


class UserWebInterfaceTestCase(unittest.TestCase):

    def setUp(self):
        web.app.config['TESTING'] = True
        web.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        core.db.create_all()
        self.app = web.app.test_client()

    def tearDown(self):
        core.db.drop_all()

    def test_register_user(self):
        form_content = {'name': 'test_user', 
                        'full_name': 'Test User',
                        'email': 'test_user@datahub.net',
                        'password': 'password',
                        'password_confirm': 'password'}
        res = self.app.post('/register', data=form_content)
        assert res.status.startswith("302"), res
        res = self.app.get('/api/v1/profile/test_user', 
                headers={'Accept': JSON})
        assert res.status.startswith("200"), res.status
        body = json.loads(res.data)
        assert body['full_name']=='Test User', body



if __name__ == '__main__':
    unittest.main()

