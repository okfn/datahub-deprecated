import unittest
import json

from datahub import core
from datahub import model
from datahub import web

from test_dataset import DATASET_FIXTURE
from test_resource import RESOURCE_FIXTURE
from util import make_test_app, tear_down_test_app
from util import create_fixture_user, AUTHZ, JSON

class SearchTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.make_fixtures()

    def tearDown(self):
        tear_down_test_app()

    def make_fixtures(self):
        create_fixture_user(self.app)
        self.app.post('/api/v1/dataset/fixture', 
                headers={'Authorization': AUTHZ},
                data=DATASET_FIXTURE)
        self.app.post('/api/v1/resource/fixture', 
                      data=RESOURCE_FIXTURE,
                      headers={'Authorization': AUTHZ})

    def test_basic_search(self):
        res = self.app.get('/search')
        assert '<h1>Search</h1>' in res.data, res.data

if __name__ == '__main__':
    unittest.main()
