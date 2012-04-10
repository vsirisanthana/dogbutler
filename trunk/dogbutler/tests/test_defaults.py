from dummycache.cache import Cache
from mock import patch
from requests.models import Response

from dogbutler import get
from dogbutler.defaults import (get_default_cache, get_default_cookie_cache, get_default_redirect_cache,
                                set_default_cache, set_default_cookie_cache, set_default_redirect_cache)
from dogbutler.tests.base import BaseTestCase


@patch('requests.sessions.Session.request')
class TestDefaults(BaseTestCase):

    def setUp(self):
        super(TestDefaults, self).setUp()
        self._orig_default_cache = get_default_cache()
        self._orig_default_cookie_cache = get_default_cookie_cache()
        self._orig_default_redirect_cache = get_default_redirect_cache()

    def tearDown(self):
        set_default_redirect_cache(self._orig_default_redirect_cache)
        set_default_cookie_cache(self._orig_default_cookie_cache)
        set_default_cache(self._orig_default_cache)
        super(TestDefaults, self).tearDown()

    def test_set_default_cache(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=100',
            }
        mock_request.return_value = response

        C0 = self.cache
        C1 = Cache()
        C2 = Cache()

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)

        set_default_cache(C1)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)

        set_default_cache(C2)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)

        set_default_cache(C0)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)

    def test_disable_default_cache(self, mock_request):
        """
        Test disable default cache (by setting default cache to None)
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=100',
            }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)

        set_default_cache(None)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 4)

    def test_set_default_cookie_cache(self, mock_request):
        response = Response()
        response.headers = {
            'Set-Cookie': 'name=value',
        }
        response.url = 'http://www.test.com/path'
        mock_request.return_value = response

        C0 = self.cookie_cache
        C1 = Cache()
        C2 = Cache()

        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)
        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', cookies={'name': 'value'}, allow_redirects=True)

        set_default_cookie_cache(C1)

        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)
        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', cookies={'name': 'value'}, allow_redirects=True)

        set_default_cookie_cache(C2)

        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)
        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', cookies={'name': 'value'}, allow_redirects=True)

        set_default_cookie_cache(C0)

        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', cookies={'name': 'value'}, allow_redirects=True)

    def test_disable_default_cookie_cache(self, mock_request):
        """
        Test disable default cookie cache (by setting default cookie cache to None)
        """
        response = Response()
        response.headers = {
            'Set-Cookie': 'name=value',
        }
        response.url = 'http://www.test.com/path'
        mock_request.return_value = response

        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)
        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', cookies={'name': 'value'}, allow_redirects=True)

        set_default_cookie_cache(None)

        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)
        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

    def test_set_default_redirect_cache(self, mock_request):
        response0 = Response()
        response0.url = 'http://www.test.com/neverseemeagain'
        response0.status_code = 301
        response0.headers = {
            'Location': 'http://www.test.com/redirect_here',
        }

        response1 = Response()
        response1.url = 'http://www.test.com/redirect_here'
        response1.status_code = 200
        response1._content = 'Mocked response content'
        response1.headers = {
            'Vary': 'Accept',
        }
        response1.history = [response0]

        mock_request.return_value = response1

        C0 = self.redirect_cache
        C1 = Cache()
        C2 = Cache()

        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_here', allow_redirects=True)

        set_default_redirect_cache(C1)

        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_here', allow_redirects=True)

        set_default_redirect_cache(C2)

        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_here', allow_redirects=True)

        set_default_redirect_cache(C0)

        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_here', allow_redirects=True)

    def test_disable_default_redirect_cache(self, mock_request):
        """
        Test disable default redirect cache (by setting default redirect cache to None)
        """
        response0 = Response()
        response0.url = 'http://www.test.com/neverseemeagain'
        response0.status_code = 301
        response0.headers = {
            'Location': 'http://www.test.com/redirect_here',
        }

        response1 = Response()
        response1.url = 'http://www.test.com/redirect_here'
        response1.status_code = 200
        response1._content = 'Mocked response content'
        response1.headers = {
            'Vary': 'Accept',
        }
        response1.history = [response0]

        mock_request.return_value = response1

        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_here', allow_redirects=True)

        set_default_redirect_cache(None)

        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        get('http://www.test.com/neverseemeagain')
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
