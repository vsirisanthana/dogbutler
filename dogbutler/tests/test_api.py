from datetime import datetime, timedelta

from dummycache import cache as dummycache_cache
from mock import patch
from requests.models import Response

from dogbutler import get
from dogbutler.tests.base import BaseTestCase


@patch('requests.sessions.Session.request')
class TestClientSideCache(BaseTestCase):
    """
    Test client-side caching mechanism
    """

    def test_get_max_age(self, mock_request):
        """
        Test that GET requests are cached according to 'max-age' value
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=1',
        }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)

        # Move time forward 1 second
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=1)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)

    def test_get_different_urls(self, mock_request):
        """
        Test that different URLs are cached separately
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        get('http://www.test.com/path/1')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path/2')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path/1')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path/3')
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path/2')
        self.assertEqual(mock_request.call_count, 3)

    def test_get_different_queries(self, mock_request):
        """
        Test that URLs with same path but different queries are cached separately
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        get('http://www.test.com/path?name=john')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path?name=emily')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path?name=john&age=30')
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path?name=emily')
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path?name=john&age=30')
        self.assertEqual(mock_request.call_count, 3)

    def test_get_different_fragments(self, mock_request):
        """
        Test that URLs with same path but different fragments are cached separately
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        get('http://www.test.com/path#help')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path#header')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path#header')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path#footer')
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path#help')
        self.assertEqual(mock_request.call_count, 3)

    def test_get_vary_on_accept(self, mock_request):
        """
        Test that GET requests are cached separately according to the 'Vary' header
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
            'Vary': 'Accept'
        }
        mock_request.return_value = response

        get('http://www.test.com/path', headers={'Accept': 'application/json'})
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path', headers={'Accept': 'application/json'})
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/path', headers={'Accept': 'application/xml'})
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/path', headers={'Accept': 'text/html'})
        self.assertEqual(mock_request.call_count, 3)
        get('http://www.test.com/path', headers={'Accept': 'application/json, */*'})
        self.assertEqual(mock_request.call_count, 4)

    def test_get_no_cache_control_header(self, mock_request):
        """
        Test that GET requests are not cached if there's no 'Cache-Control' header
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        # no cache-control header
        response.headers = {}
        mock_request.return_value = response

        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 3)

    def test_get_cache_control_no_cache(self, mock_request):
        """
        Make sure we not cache at all even there's a no-cache only at certain field
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        # no cache-control header
        response.headers = {
            'Cache-Control': 'no-cache=field, max-age=10'
        }
        mock_request.return_value = response

        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 3)

    def test_get_cache_control_no_cache_empty_field(self, mock_request):
        """
        Test that GET requests are not cached if 'no-cache' is empty
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        # no cache-control header
        response.headers = {
            'Cache-Control': 'no-cache'
        }
        mock_request.return_value = response

        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 1)
        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 2)
        get('http://www.test.com/nocache_control=True')
        self.assertEqual(mock_request.call_count, 3)

    def test_get_cache_201(self, mock_request):
        """
        Test that 201 GET responses are cached
        """
        response = Response()
        response.status_code = 201
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 201)

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 201)

    def test_get_cache_204(self, mock_request):
        """
        Test that 204 GET responses are cached
        """
        response = Response()
        response.status_code = 204
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 204)

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 204)

    def test_get_cache_400(self, mock_request):
        """
        Test that 400 GET responses are cached
        """
        response = Response()
        response.status_code = 400
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 400)

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 400)

    def test_get_cache_401(self, mock_request):
        """
        Test that 401 GET responses are cached
        """
        response = Response()
        response.status_code = 401
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 401)

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 401)

    def test_get_cache_403(self, mock_request):
        """
        Test that 403 GET responses are cached
        """
        response = Response()
        response.status_code = 403
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 403)

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 403)

    def test_get_cache_404(self, mock_request):
        """
        Test that 404 GET responses are cached
        """
        response = Response()
        response.status_code = 404
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
        }
        mock_request.return_value = response

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 404)

        response = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(response.status_code, 404)

    def test_not_return_cached_value_if_request_said_no_cache(self, mock_get):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
            'hello': 'world'
        }
        mock_get.return_value = response

        result = get('http://www.test.com/path/1', headers={'Cache-Control': 'no-cache'})
        self.assertEqual(mock_get.call_count, 1)
        result = get('http://www.test.com/path/1')
        self.assertEqual(mock_get.call_count, 1)
        result = get('http://www.test.com/path/1', headers={'Cache-Control': 'no-cache'})
        self.assertEqual(mock_get.call_count, 2)
        result = get('http://www.test.com/path/1', headers={'Cache-Control': 'no-cache'})
        self.assertEqual(mock_get.call_count, 3)

    def test_not_cache_hop_by_hop_headers(self, mock_get):
        """
        Test hop-by-hop headers are not cached
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=10',
            'euam': 'hello',
            'connection': 'abc',
            'keep-alive': '1',
            'proxy-authenticate': 'somehthing',
            'proxy-authorization': 'yo',
            'te': 'yeah',
            'trailers': 3,
            'transfer-encoding': 'text',
            'upgrade': 'true'
        }
        mock_get.return_value = response

        # assert that first time we get the response still have all of the hop-by-hop headers
        result = get('http://www.test.com/path/1')
        self.assertEqual(mock_get.call_count, 1)
        self.assertIn('connection', result.headers)
        self.assertIn('keep-alive', result.headers)
        self.assertIn('proxy-authenticate', result.headers)
        self.assertIn('proxy-authorization', result.headers)
        self.assertIn('te', result.headers)
        self.assertIn('trailers', result.headers)
        self.assertIn('transfer-encoding', result.headers)
        self.assertIn('upgrade', result.headers)

        # should not get hop-by-hop headers when get from cache
        result = get('http://www.test.com/path/1')
        self.assertEqual(mock_get.call_count, 1)
        self.assertNotIn('connection', result.headers)
        self.assertNotIn('keep-alive', result.headers)
        self.assertNotIn('proxy-authenticate', result.headers)
        self.assertNotIn('proxy-authorization', result.headers)
        self.assertNotIn('te', result.headers)
        self.assertNotIn('trailers', result.headers)
        self.assertNotIn('transfer-encoding', result.headers)
        self.assertNotIn('upgrade', result.headers)

    def test_return_hop_headers_if_not_return_from_cache(self, mock_get):
        """
        Test hop-by-hop headers are not cached
        """
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'connection': 'abc',
            'keep-alive': '1',
            'proxy-authenticate': 'somehthing',
            'proxy-authorization': 'yo',
            'te': 'yeah',
            'trailers': 3,
            'transfer-encoding': 'text',
            'upgrade': 'true'
        }
        mock_get.return_value = response

        result = get('http://www.test.com/path/1')
        self.assertEqual(mock_get.call_count, 1)
        self.assertIn('connection', result.headers)
        self.assertIn('keep-alive', result.headers)
        self.assertIn('proxy-authenticate', result.headers)
        self.assertIn('proxy-authorization', result.headers)
        self.assertIn('te', result.headers)
        self.assertIn('trailers', result.headers)
        self.assertIn('transfer-encoding', result.headers)
        self.assertIn('upgrade', result.headers)

        result = get('http://www.test.com/path/1')
        self.assertEqual(mock_get.call_count, 2)
        self.assertIn('connection', result.headers)
        self.assertIn('keep-alive', result.headers)
        self.assertIn('proxy-authenticate', result.headers)
        self.assertIn('proxy-authorization', result.headers)
        self.assertIn('te', result.headers)
        self.assertIn('trailers', result.headers)
        self.assertIn('transfer-encoding', result.headers)
        self.assertIn('upgrade', result.headers)


@patch('requests.sessions.Session.request')
class TestServerSideCache(BaseTestCase):
    """
    Test server-side caching mechanism
    """

    def test_get_if_modified_since_header(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=1',
            'Last-Modified': 'Tue, 28 Feb 2012 15:50:14 GMT',
            }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        # Move time forward 1 second
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=1)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', headers={'If-Modified-Since': 'Tue, 28 Feb 2012 15:50:14 GMT'}, allow_redirects=True)

    def test_get_if_modified_since_header_not_overridden(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=1',
            'Last-Modified': 'Tue, 28 Feb 2012 15:50:14 GMT',
            }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        # Move time forward 1 second
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=1)

        get('http://www.test.com/path', headers={'If-Modified-Since': '2011-01-11 00:00:00.000000'})
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', headers={'If-Modified-Since': '2011-01-11 00:00:00.000000'}, allow_redirects=True)

    def test_get_if_modified_since_header_no_cache(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=0',
            'Last-Modified': 'Tue, 28 Feb 2012 15:50:14 GMT',
            }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        get('http://www.test.com/path', headers={'If-Modified-Since': 'Sun, 01 Jan 2012 00:00:00 GMT'})
        self.assertEqual(mock_request.call_count, 3)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', headers={'If-Modified-Since': 'Sun, 01 Jan 2012 00:00:00 GMT'}, allow_redirects=True)

    def test_get_if_none_match_header(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=1',
            'ETag': '"fdcd6016cf6059cbbf418d66a51a6b0a"',
            }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        # Move time forward 1 second
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=1)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', headers={'If-None-Match': '"fdcd6016cf6059cbbf418d66a51a6b0a"'}, allow_redirects=True)

    def test_get_if_none_match_header_not_overridden(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'max-age=1',
            'ETag': '"fdcd6016cf6059cbbf418d66a51a6b0a"',
            }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        # Move time forward 1 second
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=1)

        get('http://www.test.com/path', headers={'If-None-Match': '"ffffffffffffffffffffffffffffffff"'})
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', headers={'If-None-Match': '"ffffffffffffffffffffffffffffffff"'}, allow_redirects=True)

    def test_get_if_modified_since_header_no_cache(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = 'Mocked response content'
        response.headers = {
            'Cache-Control': 'no-cache',
            'ETag': '"fdcd6016cf6059cbbf418d66a51a6b0a"',
            }
        mock_request.return_value = response

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        get('http://www.test.com/path', headers={'If-None-Match': '"ffffffffffffffffffffffffffffffff"'})
        self.assertEqual(mock_request.call_count, 3)
        mock_request.assert_called_with('GET', 'http://www.test.com/path', headers={'If-None-Match': '"ffffffffffffffffffffffffffffffff"'}, allow_redirects=True)

    def test_get_304(self, mock_request):
        response0 = Response()
        response0.status_code = 200
        response0._content = 'Mocked response content'
        response0.headers = {
            'Cache-Control': 'max-age=1',
            'ETag': '"fdcd6016cf6059cbbf418d66a51a6b0a"',
            }

        response1 = Response()
        response1.status_code = 304
        response1._content = ''
        response1.headers = {
            'Cache-Control': 'max-age=2',
            }
        mock_request.side_effect = [response0, response1, response1, response1]

        get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)

        # Move time forward 1 second
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=1)

        r = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        self.assertEqual(r.status_code, 304)
        self.assertEqual(r.content, 'Mocked response content')
        self.assertEqual(r.headers['Cache-Control'], 'max-age=2')

        r = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 2)
        self.assertEqual(r.status_code, 304)
        self.assertEqual(r.content, 'Mocked response content')

        # Move time forward 3 seconds (1 + 2)
        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=3)

        r = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        self.assertEqual(r.status_code, 304)
        self.assertEqual(r.content, 'Mocked response content')
        self.assertEqual(r.headers['Cache-Control'], 'max-age=2')

    def test_get_304_cache_not_exist(self, mock_request):
        response0 = Response()
        response0.status_code = 200
        response0._content = 'Mocked response content X'
        response0.headers = {
            'Cache-Control': 'max-age=10',
            'ETag': '"fdcd6016cf6059cbbf418d66a51a6b0a"',
            }

        response1 = Response()
        response1.status_code = 304
        response1._content = ''
        response1.headers = {
            'Cache-Control': 'max-age=10',
            }

        response2 = Response()
        response2.status_code = 200
        response2._content = 'Mocked response content Y'
        response2.headers = {
            'Cache-Control': 'max-age=10',
            'ETag': '"a0b6a15a66d814fbbc9506fc6106dcdf"',
            }

        mock_request.side_effect = [response0, response1, response2]

        r = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.content, 'Mocked response content X')

        self.cache.clear()

        r = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        self.assertEqual(r.content, 'Mocked response content Y')

        r = get('http://www.test.com/path')
        self.assertEqual(mock_request.call_count, 3)
        self.assertEqual(r.content, 'Mocked response content Y')


@patch('requests.sessions.Session.request')
class TestRedirect(BaseTestCase):
    """
    Test redirect mechanism
    """

    def test_get_301_only_once(self, mock_request):
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


        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        #assert we not make request to 301 again
        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_here', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

    def test_get_301_only_once_with_cache(self, mock_request):
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
            'Cache-Control': 'max-age=10',
            'Vary': 'Accept',
        }
        response1.history = [response0]

        mock_request.return_value = response1


        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        # assert we not making any call as we get result from cache
        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Mocked response content')

        # assert get the redirected url direct is working fine, and give us result from cache
        r = get('http://www.test.com/redirect_here')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Mocked response content')

    def test_get_301_thrice(self, mock_request):
        response0 = Response()
        response0.url = 'http://www.test.com/neverseemeagain'
        response0.status_code = 301
        response0.headers = {
            'Location': 'http://www.test.com/redirect_1',
            }

        response1 = Response()
        response1.url = 'http://www.test.com/redirect_1'
        response1.status_code = 301
        response1.headers = {
            'Location': 'http://www.test.com/redirect_2',
            }

        response2 = Response()
        response2.url = 'http://www.test.com/redirect_2'
        response2.status_code = 301
        response2.headers = {
            'Location': 'http://www.test.com/redirect_3',
            }

        response3 = Response()
        response3.url = 'http://www.test.com/redirect_3'
        response3.status_code = 200
        response3._content = 'Mocked response content'
        response3.headers = {
            'Vary': 'Accept',
            }
        response3.history = [response0, response1, response2]

        mock_request.return_value = response3


        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 1)
        mock_request.assert_called_with('GET', 'http://www.test.com/neverseemeagain', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        #assert we not make request to 301 again
        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_3', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        r = get('http://www.test.com/redirect_1')
        self.assertEqual(mock_request.call_count, 3)
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_3', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        r = get('http://www.test.com/redirect_2')
        self.assertEqual(mock_request.call_count, 4)
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_3', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        r = get('http://www.test.com/redirect_3')
        self.assertEqual(mock_request.call_count, 5)
        mock_request.assert_called_with('GET', 'http://www.test.com/redirect_3', allow_redirects=True)
        self.assertEqual(r.status_code, 200)

    def test_get_301_thrice_with_cache(self, mock_request):
        response0 = Response()
        response0.url = 'http://www.test.com/neverseemeagain'
        response0.status_code = 301
        response0.headers = {
            'Location': 'http://www.test.com/redirect_1',
            }

        response1 = Response()
        response1.url = 'http://www.test.com/redirect_1'
        response1.status_code = 301
        response1.headers = {
            'Location': 'http://www.test.com/redirect_2',
            }

        response2 = Response()
        response2.url = 'http://www.test.com/redirect_2'
        response2.status_code = 301
        response2.headers = {
            'Location': 'http://www.test.com/redirect_3',
            }

        response3 = Response()
        response3.url = 'http://www.test.com/redirect_3'
        response3.status_code = 200
        response3._content = 'Mocked response content'
        response3.headers = {
            'Cache-Control': 'max-age=10',
            'Vary': 'Accept',
            }
        response3.history = [response0, response1, response2]

        mock_request.return_value = response3


        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Mocked response content')

        # assert we not making any call as we get result from cache
        r = get('http://www.test.com/neverseemeagain')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Mocked response content')

        # assert get the redirected url direct is working fine, and give us result from cache
        r = get('http://www.test.com/redirect_1')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Mocked response content')

        r = get('http://www.test.com/redirect_2')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Mocked response content')

        r = get('http://www.test.com/redirect_3')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Mocked response content')


@patch('requests.sessions.Session.request')
class TestCookie(BaseTestCase):
    """
    Test cookie mechanism
    """

    def test_cookie_without_domain_and_path(self, mock_request):
        response0 = Response()
        response0.headers = {
            'Set-Cookie': 'name=value;, name2=value2; max-age=20'
        }
        response0.url = 'http://www.test.com/path0'

        response1 = Response()
        response1.headers = {
            'Set-Cookie': 'name=new_value;, name3=value3; max-age=20'
        }
        response1.url = 'http://www.test.com/path1'

        response2 = Response()
        response2.headers = {
            'Set-Cookie': 'other_name=value;, other_name2=value2; max-age=20'
        }
        response2.url = 'http://www.test.com/path2'

#        response3 = Response()
#        response3.headers = {
#            'Set-Cookie': 'name3=value3; domain=www.test.com'
#        }

#        mock_request.side_effect = [response0, response3, response0, response1, response2, response2, response0]
        mock_request.side_effect = [response0, response1, response2]

        response = get('http://www.test.com/path0')
        mock_request.assert_called_with('GET', 'http://www.test.com/path0', allow_redirects=True)

        #all later calls of same domain must send cookies in header
        response = get('http://www.test.com/path1')
        mock_request.assert_called_with('GET', 'http://www.test.com/path1', cookies={'name': 'value', 'name2': 'value2'}, allow_redirects=True)

        response = get('http://www.test.com/path2')
        mock_request.assert_called_with('GET', 'http://www.test.com/path2', cookies={'name': 'new_value', 'name2': 'value2', 'name3': 'value3'}, allow_redirects=True)

#        response = get('http://www.test.com/some_other_path2/')
#        mock_request.assert_called_with('http://www.test.com/some_other_path2/', cookies={'name2': 'value2', 'name3': 'value3', 'name': 'value'})
#
#        # other domain get no cookies
#        response = get('http://www.other_domain.com/some_other_path2/')
#        mock_request.assert_called_with('http://www.other_domain.com/some_other_path2/')
#
#        # other domain get their cookies
#        response = get('http://www.othertest.com/')
#
#        self.assertIsNotNone(self.cookie_cache.get('www.othertest.com'))
#        self.assertIsNotNone(self.cookie_cache.get('www.othertest.com.other_name'))
#        self.assertIsNotNone(self.cookie_cache.get('www.othertest.com.other_name2'))
#
#        response = get('http://www.othertest.com/some_other_path2/')
#        mock_request.assert_called_with('http://www.othertest.com/some_other_path2/', cookies={'other_name2': 'value2', 'other_name': 'value'})
#
#        #call first one again, make sure we still send cookie
#        response = get('http://www.test.com/some_other_path/')
#        mock_request.assert_called_with('http://www.test.com/some_other_path/', cookies={'name2': 'value2', 'name3': 'value3', 'name': 'value'})
#
#    def test_expired_cookie(self, mock_request):
#
#        expire_string = _getdate(future=3)
#        response = Response()
#        response.status_code = 200
#        response._content = 'Mocked response content'
#        response.headers = {
#            'Set-Cookie': 'other_name=value; expires=%s;, other_name2=value2;max-age=6' % expire_string
#        }
#        response.cookies = dict_from_string(response.headers['Set-Cookie'])
#
#
#        mock_request.return_value = response
#        response = get('http://www.othertest.com/some_other_path2/')
#
#        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=1)
#        response = get('http://www.othertest.com/some_other_path/')
#        mock_request.assert_called_with('http://www.othertest.com/some_other_path/', cookies={'other_name2': 'value2', 'other_name': 'value'})
#
#        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=4)
#        response = get('http://www.othertest.com/some_other_path/')
#        mock_request.assert_called_with('http://www.othertest.com/some_other_path/', cookies={'other_name2': 'value2'})
#
#        dummycache_cache.datetime.now = lambda: datetime.now() + timedelta(seconds=11)
#        response = get('http://www.othertest.com/some_other_path/')
#        mock_request.assert_called_with('http://www.othertest.com/some_other_path/')
#
#    def test_cookie_with_domain(self, mock_request):
#        response0 = Response()
#        response0.status_code = 200
#        response0._content = 'Mocked response content'
#        response0.headers = {
#            'Set-Cookie': 'name=value; Domain=www.test.com'
#        }
#
#        mock_request.return_value = response0
#
#        get('http://www.test.com/cookie')
#
#        #all later calls of same domain must send cookies in header
#        get('http://www.test.com/some_other_path/')
#        mock_request.assert_called_with('http://www.test.com/some_other_path/', cookies={'name': 'value'})


    def test_user_defined_cookie(self, mock_request):
        """
        Test that user-define cookie should take precedence over auto cookie
        """
        response = Response()
        response.headers = {'Set-Cookie': 'a=apple;, b=banana; max-age=20'}
        response.url = 'http://www.test.com/path'
        mock_request.return_value = response

        get('http://www.test.com/path')
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True)

        # Test that user-defined cookie is not ignored
        get('http://www.test.com/path', cookies={'c': 'citrus'})
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True,
            cookies={'a': 'apple', 'b': 'banana', 'c': 'citrus'}
        )

        # Test that user-defined cookie has higher precedence
        get('http://www.test.com/path', cookies={'a': 'anchovies'})
        mock_request.assert_called_with('GET', 'http://www.test.com/path', allow_redirects=True,
            cookies={'a': 'anchovies', 'b': 'banana'}
        )

