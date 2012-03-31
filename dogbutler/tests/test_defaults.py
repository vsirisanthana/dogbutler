from dummycache.cache import Cache
from mock import patch
from requests.models import Response

from dogbutler import get
from dogbutler.defaults import get_default_cache, set_default_cache
from dogbutler.tests.base import BaseTestCase


@patch('requests.get')
class TestDefaults(BaseTestCase):

    def setUp(self):
        super(TestDefaults, self).setUp()
        self._orig_default_cache = get_default_cache()

    def tearDown(self):
        set_default_cache(self._orig_default_cache)
        super(TestDefaults, self).tearDown()

    def test_set_default_cache(self, mock_get):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=100',
            }
        mock_get.return_value = response

        C0 = self.cache
        C1 = Cache()
        C2 = Cache()

        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 1)
        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 1)

        set_default_cache(C1)

        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 2)
        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 2)

        set_default_cache(C2)

        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 3)
        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 3)

        set_default_cache(C0)

        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 3)
        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 3)

    def test_disable_default_cache(self, mock_get):
        """
        Test disable default cache (by setting default cache to None)
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=100',
            }
        mock_get.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 1)
        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 1)

        set_default_cache(None)

        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 2)
        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 3)
        get('http://www.test.com/path')
        self.assertEqual(mock_get.call_count, 4)

