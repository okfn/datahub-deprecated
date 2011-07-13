import unittest
import json

from datahub import core
from datahub import model

from util import make_test_app, tear_down_test_app
from test_resource import RESOURCE_FIXTURE

class EventTestCase(unittest.TestCase):

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

        self.app.post('/api/v1/resource/fixtures', data=RESOURCE_FIXTURE)

    def test_resource_create_event_exists(self):
        res = self.app.get('/api/v1/event/1')
        assert res.status.startswith("200"), res.status
        body = json.loads(res.data)
        assert body['type'] == 'resource_created'


if __name__ == '__main__':
    unittest.main()

