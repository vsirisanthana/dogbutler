from requests import request, get, head, post, patch, put, delete, options, sessions
from .sessions import session

# User DogButler session instead
sessions.session = session
