from datetime import datetime, timedelta

from dummycache import cache as dummycache_cache
from mock import patch
from requests.models import Response

from dogbutler import Session
from dogbutler.tests.base import BaseTestCase


@patch('requests.sessions.Session.request')
class TestSessions(BaseTestCase):

    def test_cache(self, mock_request):
        """
        Test that each session has its own cache "sandbox".
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {'Cache-Control': 'max-age=10'}

        mock_request.return_value = response

        s0 = Session()
        s1 = Session()

        # T=0: s0 makes multiple requests. Only the 1st request should not come from cache.
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)

        # T=5: s1 makes multiple requests. Only the 1st request should not come from cache.
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=5)
        s1.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        s1.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        s1.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)

        # s0 makes multiple requests. All requests should come from cache.
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)

        # T=15: s0 makes multiple requests. Only the 1st request should not come from cache.
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=15)
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        s0.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)

        # s1 makes multiple requests. Only the 1st request should not come from cache.
        s1.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 4)
        s1.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 4)
        s1.get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 4)
