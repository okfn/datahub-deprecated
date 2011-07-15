import unittest

from flask import g

from datahub import core
from datahub import logic

from util import make_test_app, tear_down_test_app
from util import create_fixture_user

class MailTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        create_fixture_user(self.app)
        assert core.app.testing

    def tearDown(self):
        tear_down_test_app()

    def test_account_send_mail(self):
        with core.mail.record_messages() as outbox:
            account = logic.account.get('fixture')
            logic.account.send_mail(account, 'test message',
                    'foo message')
            assert len(outbox)==1, g.outbox
            msg = outbox[0]
            assert 'test message' in msg.subject, msg.subject
            assert 'foo message' in msg.body, msg.body

if __name__ == '__main__':
    unittest.main()
