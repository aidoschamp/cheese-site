import string
import random

def newSalt() -> str:
    chars = string.ascii_letters + string.digits
    salt = ''.join(random.choice(chars) for i in range(22))
    return salt