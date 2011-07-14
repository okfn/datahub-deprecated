import unittest
import json

from datahub import core
from datahub import model
from datahub import web

JSON = 'application/json'

DATASET_FIXTURE = {'name': 'world', 
                    'summary': 'A list of everything!'}

from util import make_test_app, tear_down_test_app

class DatasetTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.make_fixtures()

    def tearDown(self):
        tear_down_test_app()

    def make_fixtures(self):
        # TODO: call logic layer instead, once there is one:
        user = model.User('fixtures', 'Mr. Fixture', 'fix@ture.org',
                          'secret')
        core.db.session.add(user)
        core.db.session.commit()

        self.app.post('/api/v1/dataset/fixtures', data=DATASET_FIXTURE)

    def test_user_dataset_index(self):
        res = self.app.get('/api/v1/dataset/fixtures')
        body = json.loads(res.data)
        assert len(body)==1, body

    def test_user_dataset_create_as_json(self):
        data = json.dumps({'name': 'foo',
                           'summary': 'A foo'})
        res = self.app.post('/api/v1/dataset/fixtures', data=data, 
                headers={'Accept': JSON}, content_type=JSON,
                follow_redirects=True)
        body = json.loads(res.data)
        assert isinstance(body, dict)

    def test_user_dataset_create_as_form_data(self):
        data = {'name': 'foo',
                'summary': 'A foo'}
        res = self.app.post('/api/v1/dataset/fixtures', data=data, 
                headers={'Accept': JSON}, follow_redirects=True)
        body = json.loads(res.data)
        assert isinstance(body, dict)
        assert body['name']=='foo', body

    def test_dataset_get(self):
        res = self.app.get('/api/v1/dataset/fixtures/world')
        body = json.loads(res.data)
        assert body['name']=='world', body
        assert 'created_at' in body, body
        assert 'updated_at' in body, body

    def test_nonexistent_resource_get(self):
        res = self.app.get('/api/v1/dataset/fixtures/no-such-dataset')
        assert res.status.startswith("404"), res.status
        assert 'HTML' in res.data, res.data 

    def test_nonexistent_dataset_get_as_json(self):
        res = self.app.get('/api/v1/dataset/fixtures/no-such-dataset',
                headers={'Accept': JSON})
        assert res.status.startswith("404"), res.status
        body = json.loads(res.data)
        assert 'status' in body, body

    def test_dataset_update(self):
        data = DATASET_FIXTURE.copy() 
        data['name'] = 'mars'
        res = self.app.put('/api/v1/dataset/fixtures/no-world',
                           data=data)
        assert res.status.startswith("404"), res.data
        
        res = self.app.put('/api/v1/dataset/fixtures/world',
                           data=data)
        res = self.app.get('/api/v1/dataset/fixtures/mars')
        body = json.loads(res.data)
        assert body['name']=='mars', body

    def test_dataset_delete(self):
        res = self.app.delete('/api/v1/dataset/fixtures/no-world')
        assert res.status.startswith("404"), res.data
        
        res = self.app.delete('/api/v1/dataset/fixtures/world')
        assert res.status.startswith("410"), res.data

        res = self.app.get('/api/v1/dataset/fixtures/world')
        assert res.status.startswith("404"), res.data

    def test_create_invalid_data(self):
        data = DATASET_FIXTURE.copy() 
        data['name'] = 'invalid name'
        res = self.app.post('/api/v1/dataset/fixtures', data=data, 
                            headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data

    def test_create_missing_data(self):
        data = DATASET_FIXTURE.copy() 
        data['name'] = ''
        res = self.app.post('/api/v1/dataset/fixtures', data=data, 
                            headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data

    def test_create_existing_name(self):
        res = self.app.post('/api/v1/dataset/fixtures', 
                            data=DATASET_FIXTURE, 
                            headers={'Accept': JSON})
        assert res.status.startswith("400"), res
        data = json.loads(res.data)
        assert 'name' in data['errors'], data

    #def test_wui_dataset_get(self):
    #    res = self.app.get('/fixtures/world')
    #    assert res.status.startswith("200"), res.status
    #    assert 'A very neat dataset' in res.data, res.data



if __name__ == '__main__':
    unittest.main()


