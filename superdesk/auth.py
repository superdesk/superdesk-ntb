
import superdesk
import superdesk.utils as utils

class AuthException(Exception):
    """Base Auth Exception"""
    pass

class NotFoundAuthException(AuthException):
    """Username Not Found Auth Exception"""
    pass

class CredentialsAuthException(AuthException):
    """Credentials Not Match Auth Exception"""
    pass

def authenticate(credentials, db):
    if 'username' not in credentials:
        raise NotFoundAuthException()

    user = db.find_one('auth_users', username=credentials.get('username'))
    if not user:
        raise NotFoundAuthException()

    if not credentials.get('password') or user.get('password') != credentials.get('password'):
        raise CredentialsAuthException()

    return user

def on_create_auth(db, docs):
    for doc in docs:
        try:
            user = authenticate(doc, db)
            doc['user'] = user.get('_id')
            doc['token'] = utils.get_random_string(40)
        except NotFoundAuthException:
            superdesk.abort(404)
        except CredentialsAuthException:
            superdesk.abort(403)

superdesk.connect('create:auth', on_create_auth)

superdesk.domain('auth_users', {
    'datasource': {
        'source': 'users'
    },
    'schema': {
        'username': {
            'type': 'string',
        },
        'password': {
            'type': 'string',
        }
    },
    'item_methods': [],
    'resource_methods': []
})

superdesk.domain('auth', {
    'schema': {
        'username': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        },
        'token': {
            'type': 'string'
        },
        'user': {
            'type': 'objectid'
        }
    },
    'resource_methods': ['POST'],
    'item_methods': ['GET'],
    'public_methods': ['POST'],
    'extra_response_fields': ['username', 'token']
})
