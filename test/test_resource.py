import unittest
import json

from datadeck import core
from datadeck import web

JSON = 'application/json'

RESOURCE_FIXTURE = {'name': 'my-file'}

class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        web.app.config['TESTING'] = True
        web.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        core.db.create_all()
        self.app = web.app.test_client()
        self.make_fixtures()

    def tearDown(self):
        core.db.drop_all()

    def make_fixtures(self):
        self.app.post('/api/v1/resource/fixtures', data=RESOURCE_FIXTURE)

    def test_user_resource_index(self):
        res = self.app.get('/api/v1/resource/no_user')
        body = json.loads(res.data)
        assert len(body)==0, body

    def test_user_resource_create_as_json(self):
        data = json.dumps({'name': 'world'})
        res = self.app.post('/api/v1/resource/hello', data=data, 
                headers={'Accept': JSON}, content_type=JSON)
        body = json.loads(res.data)
        assert isinstance(body, dict)

    def test_user_resource_create_as_form_data(self):
        data = {'name': 'world'}
        res = self.app.post('/api/v1/resource/hello', data=data, 
                headers={'Accept': JSON})
        body = json.loads(res.data)
        assert isinstance(body, dict)
        assert body['name']=='world', body

    def test_resource_get(self):
        res = self.app.get('/api/v1/resource/fixtures/my-file')
        body = json.loads(res.data)
        assert body['name']=='my-file', body
    
    def test_nonexistent_resource_get(self):
        res = self.app.get('/api/v1/resource/fixtures/no-such-file')
        assert res.status.startswith("404"), res.status


if __name__ == '__main__':
    unittest.main()

