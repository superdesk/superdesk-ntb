import flask
import superdesk

from werkzeug.datastructures import MultiDict
from flask import current_app as app, request
from eve.utils import ParsedRequest
from feedgen import feed


blueprint = flask.Blueprint('rss', __name__)


def generate_rss(items):
    fg = feed.FeedGenerator()
    fg.title('Newshub feed')
    fg.link(href=flask.url_for('rss.index', _external=True), rel='self')
    fg.description('foo')
    for item in items:
        entry = fg.add_entry()
        entry.id(item['_id'])
        entry.title(item.get('headline', item.get('name', item.get('slugline', ''))))
        entry.description(item.get('description_text'))
        entry.published(item['_created'])
        entry.updated(item['versioncreated'])
        entry.content(item.get('body_html'), type='text/html')
    return fg.rss_str(pretty=True)


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

    content = generate_rss(items)
    return flask.Response(content, mimetype='application/rss+xml')


def init_app(_app):
    _app.register_blueprint(blueprint, url_prefix='/rss')
