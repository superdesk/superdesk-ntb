import flask
import superdesk

from werkzeug.datastructures import MultiDict
from flask import current_app as app, request
from eve.utils import ParsedRequest


blueprint = flask.Blueprint('rss', __name__)


@blueprint.route('/')
def index():
    auth = app.auth
    if not auth.authorized([], 'items', request.method):
        return auth.authenticate()
    req = ParsedRequest()
    req.args = MultiDict()
    res = superdesk.get_resource_service('items').get(req, {})
    items = []
    for item in res:
        items.append(item)
    return flask.jsonify(items)


def init_app(_app):
    _app.register_blueprint(blueprint, url_prefix='/rss')
