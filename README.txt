====================
 READ ME
====================

Dogbutler is a client library base on requests but with a cache and persistent cookie support.

====================
    INSTALLATION
====================
>>> pip install dogbutler

====================
       USAGE
====================
DogButler supports GET, HEAD, POST, PATCH, PUT, DELETE, and OPTIONS requests.

>>> import dogbutler
>>> r = dogbutler.get('http://www.google.com', headers={'a': 'antelope'}, cookies={'a': 'apple'})
>>> r.status_code
200
>>> r.content

Sessions
--------------------
A session has its own cache, cookie jar, and redirect history.

>>> from dogbutler import Session
>>> s = Session()
>>> r = s.get('http://www.google.com', headers={'a': 'antelope'}, cookies={'a': 'apple'})
>>> r.status_code
200
>>> r.content

Async
--------------------
*Note: Only GET requests can be called asynchronously at the moment.*

Each request is a tuple of (url, kwargs), where kwargs can contain optional arguments such as headers and cookies.

>>> from dogbutler import async
>>> request1 = ('http://www.google.com', {'headers': {'a': 'antelope'}, 'cookies': {'a': 'apple'}})
>>> request2 = ('http://www.apple.com', {'headers': {'b': 'bear'}, 'cookies': {'b': 'banana'}})
>>> response1, response2 = async.get([request1, request2])
>>> response1.status_code
200
>>> response2.status_code
200

====================
     CHANGE LOG
====================
Version 0.0.4
--------------------
- Ignore cache if no-cache is defined in request header.
- Fix minor bugs.

Version 0.0.3
--------------------
- Support Sessions.
- Not cache hop-by-hop headers.

Version 0.0.2
--------------------
- Set default cache, cookie cache, and redirect cache backends.
- Disable cache, cookie cache, and redirect cache by setting each to None.

Version 0.0.1
--------------------
- Initial release.