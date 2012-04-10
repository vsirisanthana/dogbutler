from requests.sessions import Session as requests_Session

from .cache import CacheManager
from .cookie import CookieManager
from .defaults import get_default_cache, get_default_cookie_cache, get_default_redirect_cache
from .models import Request
from .redirect import RedirectManager
from .utils.rand import random_string


class Session(requests_Session):

    def __init__(self, **kwargs):
        self.key_prefix = kwargs.pop('key_prefix') if 'key_prefix' in kwargs else random_string(64)
        super(Session, self).__init__(**kwargs)

    def request(self, method, url, queue=None, **kwargs):

        method = str(method).upper()
        if method == 'GET':

            # Create managers
            cache_manager = CacheManager(cache=get_default_cache(), key_prefix=self.key_prefix)
            cookie_manager = CookieManager(cache=get_default_cookie_cache(), key_prefix=self.key_prefix)
            redirect_manager = RedirectManager(cache=get_default_redirect_cache(), key_prefix=self.key_prefix)

            # Convert to Request object
            request = Request(url, method=method, **kwargs)

            # Process request
            redirect_manager.process_request(request)                   # Redirect if previously got 301
            cookie_manager.process_request(request)                     # Set cookies
            response = cache_manager.process_request(request)           # Get from cache if conditions are met
            if response is not None:
                if queue: queue.put(response)
                return response

            # Update kwargs
            if request.headers: kwargs['headers'] = request.headers     # Update kwargs with new headers
            if request.cookies: kwargs['cookies'] = request.cookies     # Update kwargs with new cookies

            # Make a request
            response = super(Session, self).request(method, request.url, **kwargs)

            # Process response
            redirect_manager.process_response(request, response)        # Save redirect info

            # Handle 304
            if response.status_code == 304:
                response = cache_manager.process_304_response(request, response)
                if response is None:
                    if kwargs.has_key('If-Modified-Since'): del kwargs['If-Modified-Since']
                    if kwargs.has_key('If-None-Match'): del kwargs['If-None-Match']
                    response = super(Session, self).get(request.url, **kwargs)

            cookie_manager.process_response(request, response)          # Handle cookie
            cache_manager.process_response(request, response)           # Update cache as necessary

        else:
            response = super(Session, self).request(method, url, **kwargs)

        if queue: queue.put(response)
        return response


def session(**kwargs):
    """Returns a :class:`Session` for context-management."""

    return Session(**kwargs)
