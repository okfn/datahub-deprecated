import unittest
import json

from datahub import core
from datahub import model
from datahub import web

JSON = 'application/json'

RESOURCE_FIXTURE = {'name': 'my-file', 
                    'url': 'http://mylab.org/data.csv',
                    'summary': 'A very neat resource!'}

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
        # TODO: call logic layer instead, once there is one:
        user = model.User('fixtures', 'Mr. Fixture', 'fix@ture.org',
                          'secret')
        core.db.session.add(user)
        core.db.session.commit()

        self.app.post('/api/v1/resource/fixtures', data=RESOURCE_FIXTURE)

    def test_user_resource_index(self):
        res = self.app.get('/api/v1/resource/fixtures')
        body = json.loads(res.data)
        assert len(body)==1, body

    def test_user_resource_create_as_json(self):
        data = json.dumps({'name': 'world', 'url': 'http://foos.com', 
                           'summary': 'A foo'})
        res = self.app.post('/api/v1/resource/fixtures', data=data, 
                headers={'Accept': JSON}, content_type=JSON,
                follow_redirects=True)
        body = json.loads(res.data)
        assert isinstance(body, dict)

    def test_user_resource_create_as_form_data(self):
        data = {'name': 'world', 'url': 'http://foos.com', 
                'summary': 'A foo'}
        res = self.app.post('/api/v1/resource/fixtures', data=data, 
                headers={'Accept': JSON}, follow_redirects=True)
        body = json.loads(res.data)
        assert isinstance(body, dict)
        assert body['name']=='world', body

    def test_resource_get(self):
        res = self.app.get('/api/v1/resource/fixtures/my-file')
        body = json.loads(res.data)
        assert body['name']=='my-file', body
        assert 'created_at' in body, body
        assert 'updated_at' in body, body
    
    def test_nonexistent_resource_get(self):
        res = self.app.get('/api/v1/resource/fixtures/no-such-file')
        assert res.status.startswith("404"), res.status
        assert 'HTML' in res.data, res.data 

    def test_nonexistent_resource_get_as_json(self):
        res = self.app.get('/api/v1/resource/fixtures/no-such-file',
                headers={'Accept': JSON})
        assert res.status.startswith("404"), res.status
        body = json.loads(res.data)
        assert 'status' in body, body

    def test_resource_update(self):
        data = RESOURCE_FIXTURE.copy() 
        data['name'] = 'thy-file'
        res = self.app.put('/api/v1/resource/fixtures/no-file',
                           data=data)
        assert res.status.startswith("404"), res.data
        
        res = self.app.put('/api/v1/resource/fixtures/my-file',
                           data=data)
        res = self.app.get('/api/v1/resource/fixtures/thy-file')
        body = json.loads(res.data)
        assert body['name']=='thy-file', body

    def test_resource_delete(self):
        res = self.app.delete('/api/v1/resource/fixtures/no-file')
        assert res.status.startswith("404"), res.data
        
        res = self.app.delete('/api/v1/resource/fixtures/my-file')
        assert res.status.startswith("410"), res.data

        res = self.app.get('/api/v1/resource/fixtures/my-file')
        assert res.status.startswith("404"), res.data

    def test_create_invalid_data(self):
        data = RESOURCE_FIXTURE.copy() 
        data['name'] = 'invalid name'
        res = self.app.post('/api/v1/resource/fixtures', data=data, 
                            headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data

        data = RESOURCE_FIXTURE.copy() 
        data['url'] = 'not really a url'
        res = self.app.post('/api/v1/resource/fixtures', data=data, 
                            headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'url' in data['errors'], data

    def test_create_existing_name(self):
        res = self.app.post('/api/v1/resource/fixtures', 
                            data=RESOURCE_FIXTURE, 
                            headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data




if __name__ == '__main__':
    unittest.main()

