from requests import request, get, head, post, patch, put, delete, options, sessions
from .sessions import session

DEFAULT_KEY_PREFIX = 'GVRYCH0LK79KL5QV394QP27CRO2YDGKT6JGCEPNRIDPR2O60W9TAD7A2Z7FA11BY'

# User DogButler session instead
sessions.session = lambda **kwargs: session(key_prefix=DEFAULT_KEY_PREFIX, **kwargs)
