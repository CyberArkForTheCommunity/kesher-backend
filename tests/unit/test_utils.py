import random
import string


def random_string(n=8):
    return ''.join(random.choices(string.ascii_letters, k=n))