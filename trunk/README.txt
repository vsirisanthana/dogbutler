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
>>> import dogbutler
>>> r = dogbutler.get('http://www.google.com', headers={'name': 'value'})
>>> r.status_code
200
>>> r.content

====================
     CHANGE LOG
====================
Version 0.0.3
--------------------
- Support Sessions.
- Not cache hop-by-hop headers

Version 0.0.2
--------------------
- Set default cache, cookie cache, and redirect cache backends.
- Disable cache, cookie cache, and redirect cache by setting each to None.

Version 0.0.1
--------------------
- Initial release