====================
 READ ME, READ ME!!
====================

all the interesting & useful info goes here!!!

====================
    INSTALLATION
====================
to use dogbutler simply just do::

>> pip install dogbutler

====================
       USAGE
====================
::

>> import dogbutler
>> r = dogbutler.get('http://www.google.com', headers={'name': 'value'})
>> r.status_code
200
>> r.content

====================
     CHANGE LOG
====================
Version 0.0.2
--------------------
- Set default cache, cookie cache, and redirect cache backends.
- Disable cache, cookie cache, and redirect cache by setting each to None.

Version 0.0.1
--------------------
- Initial release