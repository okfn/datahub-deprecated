import unittest
import json

from datahub import core
from datahub import model
from datahub import web

JSON = 'application/json'

RESOURCE_FIXTURE = {'name': 'my-file', 
                    'url': 'http://mylab.org/data.csv',
                    'summary': 'A very neat resource!'}

from util import make_test_app, tear_down_test_app
from util import create_fixture_user, AUTHZ

class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.make_fixtures()

    def tearDown(self):
        tear_down_test_app()

    def make_fixtures(self):
        create_fixture_user(self.app)
        self.app.post('/api/v1/resource/fixture', 
                      data=RESOURCE_FIXTURE,
                      headers={'Authorization': AUTHZ})

    def test_user_resource_index(self):
        res = self.app.get('/api/v1/resource/fixture')
        body = json.loads(res.data)
        assert len(body)==1, body

    def test_user_resource_create_as_json(self):
        data = json.dumps({'name': 'world', 'url': 'http://foos.com', 
                           'summary': 'A foo'})
        res = self.app.post('/api/v1/resource/fixture', data=data, 
                headers={'Accept': JSON, 'Authorization': AUTHZ}, 
                content_type=JSON,
                follow_redirects=True)
        body = json.loads(res.data)
        assert isinstance(body, dict)

    def test_user_resource_create_as_form_data(self):
        data = {'name': 'world', 'url': 'http://foos.com', 
                'summary': 'A foo'}
        res = self.app.post('/api/v1/resource/fixture', data=data, 
                headers={'Accept': JSON, 'Authorization': AUTHZ}, 
                follow_redirects=True)
        body = json.loads(res.data)
        assert isinstance(body, dict)
        assert body['name']=='world', body
    
    def test_user_resource_create_no_auth(self):
        data = {'name': 'world', 'url': 'http://foos.com', 
                'summary': 'A foo'}
        res = self.app.post('/api/v1/resource/fixture', data=data, 
                headers={'Accept': JSON}, 
                follow_redirects=True)
        assert res.status.startswith("403"), res.status
    
    #def test_user_resource_create_in_wui(self):
    #    data = {'name': 'world', 'url': 'http://foos.com', 
    #            'summary': 'A foo'}
    #    res = self.app.post('/resource', data=data, 
    #            follow_redirects=True, 
    #            environ_base={'REMOTE_USER': 'fixtures'})
    #    assert 'A foo' in res.data, res.data

    def test_resource_get(self):
        res = self.app.get('/api/v1/resource/fixture/my-file')
        body = json.loads(res.data)
        assert body['name']=='my-file', body
        assert 'created_at' in body, body
        assert 'updated_at' in body, body
    
    def test_nonexistent_resource_get(self):
        res = self.app.get('/api/v1/resource/fixture/no-such-file')
        assert res.status.startswith("404"), res.status
        assert 'HTML' in res.data, res.data 

    def test_nonexistent_resource_get_as_json(self):
        res = self.app.get('/api/v1/resource/fixture/no-such-file',
                headers={'Accept': JSON, 'Authorization': AUTHZ})
        assert res.status.startswith("404"), res.status
        body = json.loads(res.data)
        assert 'status' in body, body

    def test_resource_update(self):
        data = RESOURCE_FIXTURE.copy() 
        data['name'] = 'thy-file'
        res = self.app.put('/api/v1/resource/fixture/no-file',
                           headers={'Authorization': AUTHZ}, 
                           data=data)
        assert res.status.startswith("404"), res.data
        
        res = self.app.put('/api/v1/resource/fixture/my-file',
                           data=data)
        assert res.status.startswith("403"), res.data
        
        res = self.app.put('/api/v1/resource/fixture/my-file',
                           headers={'Authorization': AUTHZ}, 
                           data=data)
        res = self.app.get('/api/v1/resource/fixture/thy-file')
        body = json.loads(res.data)
        assert body['name']=='thy-file', body

    def test_resource_delete(self):
        res = self.app.delete('/api/v1/resource/fixture/no-file',
                headers={'Authorization': AUTHZ})
        assert res.status.startswith("404"), res.data
        
        res = self.app.delete('/api/v1/resource/fixture/my-file',
                headers={'Authorization': AUTHZ})
        assert res.status.startswith("410"), res.data

        res = self.app.get('/api/v1/resource/fixture/my-file')
        assert res.status.startswith("404"), res.data

    def test_create_invalid_data(self):
        data = RESOURCE_FIXTURE.copy() 
        data['name'] = 'invalid name'
        res = self.app.post('/api/v1/resource/fixture', data=data, 
                            headers={'Accept': JSON, 'Authorization': AUTHZ})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data

        data = RESOURCE_FIXTURE.copy() 
        data['url'] = 'not really a url'
        res = self.app.post('/api/v1/resource/fixture', data=data, 
                            headers={'Accept': JSON, 'Authorization': AUTHZ})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'url' in data['errors'], data

    def test_create_missing_data(self):
        data = RESOURCE_FIXTURE.copy()
        data['name'] = 'foo'
        data['url'] = ''
        res = self.app.post('/api/v1/resource/fixture', data=data, 
                            headers={'Accept': JSON, 'Authorization': AUTHZ})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'url' in data['errors'], data

        data = RESOURCE_FIXTURE.copy() 
        data['name'] = ''
        res = self.app.post('/api/v1/resource/fixture', data=data, 
                            headers={'Accept': JSON, 'Authorization': AUTHZ})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data

    def test_create_existing_name(self):
        res = self.app.post('/api/v1/resource/fixture', 
                            data=RESOURCE_FIXTURE, 
                            headers={'Accept': JSON, 'Authorization': AUTHZ})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data

    def test_wui_resource_get(self):
        res = self.app.get('/fixture/my-file')
        assert res.status.startswith("200"), res.status
        assert 'A very neat resource' in res.data, res.data


if __name__ == '__main__':
    unittest.main()

