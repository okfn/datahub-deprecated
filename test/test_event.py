import unittest
import json

from datahub import core
from datahub import model

from util import make_test_app, tear_down_test_app
from util import create_fixture_user, AUTHZ
from test_resource import RESOURCE_FIXTURE

class EventTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.make_fixtures()

    def tearDown(self):
        tear_down_test_app()

    def make_fixtures(self):
        create_fixture_user(self.app)
        self.app.post('/api/v1/resource/fixture', 
                headers={'Authorization': AUTHZ},
                data=RESOURCE_FIXTURE)

    def test_resource_create_event_exists(self):
        res = self.app.get('/api/v1/event/2')
        assert res.status.startswith("200"), res.status
        body = json.loads(res.data)
        assert body['type'] == 'resource_created'

    def test_event_does_not_exist(self):
        res = self.app.get('/api/v1/event/1022')
        assert res.status.startswith("404"), res.status

    def test_existing_event_stream(self):
        res = self.app.get('/api/v1/stream/node/1')
        assert res.status.startswith("200"), res.status
        body = json.loads(res.data)
        assert len(body)==1, body
        assert body[0]['type'] == 'resource_created', body

    def test_nonexisting_event_stream(self):
        res = self.app.get('/api/v1/stream/node/1022')
        assert res.status.startswith("200"), res.status
        body = json.loads(res.data)
        assert len(body)==0, body

class EventFeedTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.make_fixtures()

    def tearDown(self):
        tear_down_test_app()

    def make_fixtures(self):
        create_fixture_user(self.app)
        self.app.post('/api/v1/resource/fixture', 
                headers={'Authorization': AUTHZ},
                data=RESOURCE_FIXTURE)

    def test_feed_for_user(self):
        res = self.app.get('/fixture.atom')
        assert '<entry>' in res.data, res.data
        assert RESOURCE_FIXTURE['name'] in res.data, res.data
        assert '<summary type="html">%s</summary' % \
                RESOURCE_FIXTURE['summary'] in res.data, res.data

    def test_feed_for_node(self):
        res = self.app.get('/fixture/my-file.atom')
        assert '<entry>' in res.data, res.data
        assert RESOURCE_FIXTURE['name'] in res.data, res.data
        assert '<summary type="html">%s</summary' % \
                RESOURCE_FIXTURE['summary'] in res.data, res.data



if __name__ == '__main__':
    unittest.main()

