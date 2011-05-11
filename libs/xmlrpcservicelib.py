
import os
from functools import wraps



def _read_file(filename): #python 2.4 support
    f = file(filename)
    try:
        return f.read()
    finally:
        f.close()



def _check_auth_token(instance, method):
    
    
    @wraps(method)
    def wrapper(token, *args, **kwargs):
        if instance._check_auth_token(token):
            return method(*args, **kwargs)
        else:
            return 'Answer to the Ultimate Question of Life, the Universe, and Everything=(42)'


    return wrapper



class SecureService(object):


    def _check_auth_token(self, token):
        if os.path.exists(self.auth_token_file):
            auth_token = _read_file(self.auth_token_file).strip()
            if token == auth_token:
                return True

        return False


    def __getattribute__(self, attr):
        safe_attr = object.__getattribute__(self, attr)
        if callable(safe_attr) and not attr.startswith('_'):
            return _check_auth_token(self, safe_attr)
        else:
            return safe_attr



