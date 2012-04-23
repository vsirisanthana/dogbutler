from base import BaseTestCase
from dogbutler.cache import CacheManager
from dogbutler.models import Request


class TestCache(BaseTestCase):

    def setUp(self):
        super(TestCache, self).setUp()
        self.cache_manager = CacheManager(key_prefix='test_cache', cache=self.cache)

    def test_check_cache_ignore_post_request(self):
        """
        Do not check cache if request method is POST
        """
        request = Request('http://www.test.com/path', method='POST')
        response = self.cache_manager.check_cache(request)
        self.assertIsNone(response)
        self.assertFalse(request._cache_update_cache)

    def test_check_cache_ignore_put_request(self):
        """
        Do not check cache if request method is PUT
        """
        request = Request('http://www.test.com/path', method='PUT')
        response = self.cache_manager.check_cache(request)
        self.assertIsNone(response)
        self.assertFalse(request._cache_update_cache)

    def test_check_cache_ignore_delete_request(self):
        """
        Do not check cache if request method is DELETE
        """
        request = Request('http://www.test.com/path', method='DELETE')
        response = self.cache_manager.check_cache(request)
        self.assertIsNone(response)
        self.assertFalse(request._cache_update_cache)