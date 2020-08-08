import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import os


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_authorization_header():
    if('authorization' not in request.headers):
        raise AuthError({'code': 'authorization_header',
                        'description': 'authorization is missing'}, 401)

    print(request.headers['authorization'])
    auth = request.headers['authorization'].split()
    print('auth')
    print(auth)

    if(len(auth) != 2 or auth[0].lower() != 'bearer'):
        raise AuthError({'code': 'invalid hearder',
                        'description': 'authorization header must be Bearer'},
                        401)

    return auth[1]


def check_permission(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({'code': 'invalid header',
                         'description': 'permissions is missing'}, 401)

    if permission not in payload['permissions']:
        raise AuthError({'code': 'unathorized',
                        'description': 'permissions is not granted'}, 403)

    return True


def verify_token(token):
    # get the puplic key ID
    print('url')
    algorithms = os.environ['ALGORITHMS']
    API_AUDIENCE = os.environ['API_AUDIENCE']
    AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
    print(AUTH0_DOMAIN)

    url = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(url.read())
    print(url)
    print(jwks)

    # define the key dictonary to verify the token
    key_set = {}
    # claim_key = {}

    print('key_set')
    print(key_set)
    unverified_header = jwt.get_unverified_header(token)
    if unverified_header['kid'] is None:
        raise AuthError({'code': 'invalid header',
                        'description': 'invalid header'}, 401)
    print(unverified_header)

    # use key sets from public key to set the value of key claim
    for key in jwks['keys']:
        if unverified_header['kid'] == key['kid']:
            key_set = key

    print('key_set')
    print(key_set)

    if key_set:
        try:
            print(algorithms)
            print(API_AUDIENCE)
            payload = jwt.decode(token, key_set, algorithms=algorithms,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')
            return payload
        except jwt.ExpiredSignatureError:
                raise AuthError({'code': 'invalid header',
                                 'description': 'expired token'}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({'code': 'invalid header',
                             'description': 'invalid claim'}, 401)

    raise AuthError({'code': 'invalid header',
                     'description': 'invalid header'}, 401)


def require_auth(permission=''):
    def require_auth_decorator(f):
        @wraps(f)
        def wrapper(*arg, **kwargs):
            token = get_token_authorization_header()
            try:
                payload = verify_token(token)
            except:
                raise AuthError({'code': 'invalid header',
                                 'description': 'invalid token'}, 401)

            check_permission(permission, payload)

            return f(*arg, **kwargs)

        return wrapper
    return require_auth_decorator
