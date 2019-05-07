import flask
import superdesk

from flask import current_app as app, request
from eve.utils import ParsedRequest
from feedgen import feed


blueprint = flask.Blueprint('rss', __name__)


def generate_rss(items):
    fg = feed.FeedGenerator()
    fg.title('Superdesk')
    fg.id('msn-feed')
    fg.link(href=flask.url_for('rss.index', _external=True), rel='self')
    fg.description('foo')
    for item in items:
        entry = fg.add_entry()
        entry.guid(item['_id'])
        entry.title(item.get('headline', item.get('name', item.get('slugline', ''))))
        entry.pubDate(item.get('firstpublished'))
        entry.updated(item['versioncreated'])
        entry.content(get_content(item), type='CDATA')

        if item.get('description_text'):
            entry.summary(item['description_text'])

    return fg.atom_str(pretty=True)


def get_content(item):
    html = item.get('body_html', '<p></p>')
    if item.get('associations', {}):
        if item.get('featuremedia'):
            media = item['associations']['featuremedia']
            original = media.get('renditions', {}).get('original')
            if original.get('href'):
                html += '\n<img src="{}" alt="{}" title="{}" />'.format(
                    original['href'],
                    media.get('headline'),
                    media.get('headline'),
                )
    return html


@blueprint.route('/')
def index():
    auth = app.auth
    if not auth.authorized([], 'items', request.method):
        return auth.authenticate()
    req = ParsedRequest()
    req.args = request.args
    res = superdesk.get_resource_service('items').get(req, {})
    items = []
    for item in res:
        items.append(item)

    content = generate_rss(items)
    return flask.Response(content, mimetype='application/rss+xml')


def init_app(_app):
    _app.register_blueprint(blueprint, url_prefix='/rss')
