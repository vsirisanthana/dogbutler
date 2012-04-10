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

    def test_cookie(self, mock_request):
        """
        Test that each session has its own cookie "sandbox".
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {'Set-Cookie': 'name=value'}
        response.url = 'http://www.test.com/path'

        mock_request.return_value = response

        s0 = Session()
        s1 = Session()

        # s0 make requests
        s0.get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)
        s0.get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True, cookies={'name': 'value'})

        # s1 make requests
        s1.get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)
        s1.get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True, cookies={'name': 'value'})

        # s0 make requests again
        s0.get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True, cookies={'name': 'value'})
        s0.get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True, cookies={'name': 'value'})

    def test_redirect(self, mock_request):
        """
        Test that each session has its own redirect "sandbox".
        """
        response0 = Response()
        response0.url = 'http://www.test.com/neverseemeagain'
        response0.status_code = 301
        response0.headers = {'Location': 'http://www.test.com/redirect_1'}

        response1 = Response()
        response1.url = 'http://www.test.com/redirect_1'
        response1.status_code = 301
        response1.headers = {'Location': 'http://www.test.com/redirect_2'}

        response2 = Response()
        response2.url = 'http://www.test.com/redirect_2'
        response2.status_code = 301
        response2.headers = {'Location': 'http://www.test.com/redirect_3'}

        response3 = Response()
        response3.url = 'http://www.test.com/redirect_3'
        response3.status_code = 200
        response3._content = 'Mocked response content'
        response3.history = [response0, response1, response2]

        mock_request.return_value = response3

        s0 = Session()
        s1 = Session()

        # s0 make a request
        r = s0.get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        # s0 make a request again. Assert we not make request to 301 again.
        r = s0.get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_3', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        # s1 make a request
        r = s1.get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        # s1 make a request again. Assert we not make request to 301 again.
        r = s1.get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_3', allow_redirects=True)
        self.assertEqual(r.status_code, 200)