import datetime

#functions file
#Total user list and total emoji list are just one big strings, we need to capture the essense in arrays
def extract_from_sting(string):
    array = string.split(', ')
    return array

#Keys in arango can only have '_' exept of letters
import re

def make_valid_key(key):
    # Use a regular expression to match any characters that are not letters, numbers, or underscores
    return re.sub(r'[^a-zA-Z0-9_]+', '_', key)

#normalize discord timestemps
def isoformat(dt=None):
    if dt is None or not dt:
        return datetime.datetime.now()
    return getattr(dt, 'isoformat', lambda x: None)()
