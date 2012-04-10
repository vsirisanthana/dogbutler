import random
import string

def random_string(n):
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in xrange(n))