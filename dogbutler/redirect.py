from requests.exceptions import TooManyRedirects


DEFAULT_REDIRECT_KEY_PREFIX = 'redirect'
DEFAULT_REDIRECT_MAX_AGE = 60 * 60 * 24 * 365 * 10       # 10 years


class RedirectManager(object):

    def __init__(self, cache, key_prefix=''):
        self.key_prefix = '.'.join([key_prefix, DEFAULT_REDIRECT_KEY_PREFIX])
        self.cache = cache

    def get_cache_key(self, url):
        return '.'.join([self.key_prefix, url])

    def process_request(self, request):
        if self.cache is None:
            return

        url = request.url
        history = []
        while True:
            if url in history:
                raise TooManyRedirects()
            redirect_to = self.cache.get(self.get_cache_key(url))
            if redirect_to is None:
                break
            url = redirect_to
        request.url = url

    def process_response(self, request, response):
        if self.cache is None:
            return

        if response.history:
            request.url = response.url
            for r in response.history:
                if r.status_code == 301:
                    #TODO: handle case of no Location header
                    redirect_to = r.headers.get('Location')
                    self.cache.set(self.get_cache_key(r.url), redirect_to, DEFAULT_REDIRECT_MAX_AGE)
