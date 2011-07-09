import unittest

from datadeck import web

class WebstoreTestCase(unittest.TestCase):

    def setUp(self):
        web.app.config['TESTING'] = True
        web.app.config['MONGO_DB'] = 'datadeck_unittest'
        self.app = web.app.test_client()
        self.make_fixtures()

    def tearDown(self):
        pass

    def make_fixtures(self):
        pass

    def test_nothing(self):
        assert True


if __name__ == '__main__':
    unittest.main()

