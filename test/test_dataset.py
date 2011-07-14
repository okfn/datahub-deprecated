import unittest
import json

from datahub import core
from datahub import model
from datahub import web

JSON = 'application/json'

RESOURCE_FIXTURE = {'name': 'world', 
                    'summary': 'A list of everything!'}

from util import make_test_app, tear_down_test_app

class ResourceTestCase(unittest.TestCase):

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

        self.app.post('/api/v1/dataset/fixtures', data=RESOURCE_FIXTURE)

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

if __name__ == '__main__':
    unittest.main()


