import unittest
import json

from datadeck import core
from datadeck import web

class WebstoreTestCase(unittest.TestCase):

    def setUp(self):
        web.app.config['TESTING'] = True
        web.app.config['SQLALCHEMY_URL'] = 'sqlite:///:memory:'
        core.db.create_all()
        self.app = web.app.test_client()
        self.make_fixtures()

    def tearDown(self):
        core.db.drop_all()

    def make_fixtures(self):
        pass

    def test_user_resource_index(self):
        res = self.app.get('/api/v1/resource/no_user')
        body = json.loads(res.data)
        assert len(body)==0, body


if __name__ == '__main__':
    unittest.main()

