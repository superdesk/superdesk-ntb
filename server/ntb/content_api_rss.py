import re
import flask
import superdesk

from lxml import etree
from feedgen import feed
from flask import current_app as app, request
from eve.utils import ParsedRequest


blueprint = flask.Blueprint('rss', __name__)
parser = etree.HTMLParser(recover=True)


def generate_feed(items):
    fg = feed.FeedGenerator()
    fg.title('Superdesk')
    fg.id(flask.url_for('rss.index', _external=True))
    fg.link(href=flask.url_for('rss.index', _external=True), rel='self')
    fg.description('foo')
    for item in items:
        entry = fg.add_entry()
        entry.guid('{}/{}'.format(flask.url_for('rss.index', _external=True), item['_id']))
        entry.title(item.get('headline', item.get('name', item.get('slugline', ''))))
        entry.pubDate(item.get('firstpublished'))
        entry.updated(item['versioncreated'])
        entry.content(get_content(item), type='CDATA')

        category = [{'term': s.get('name')} for s in item.get('subject', []) if s.get('scheme') == 'category']
        if category:
            entry.category(category)

        if item.get('description_text'):
            entry.summary(item['description_text'])

        if item.get('byline'):
            entry.author({'name': item['byline']})

    return fg.atom_str(pretty=True) \
        .replace(b'<content type="CDATA">', b'<content type="html">')


def get_content(item):
    assoc = item.get('associations') or {}
    html = item.get('body_html', '<p></p>')
    tree = etree.fromstring(html, parser=parser)
    body = tree[0]
    for elem in body:
        if elem.tag is etree.Comment and elem.text:
            m = re.fullmatch(r'EMBED START Image {id: "([-_a-z0-9]+)"}', elem.text.strip())
            if m:
                _id = m.group(1)
                related = assoc.get(_id)
                if related and related.get('renditions') and related['renditions'].get('original'):
                    img = elem.getnext().find('img')
                    img.attrib['src'] = related['renditions']['original']['href']
                    img.attrib['alt'] = related.get('description_text')
    return etree.tostring(body, method='html') \
        .decode('utf-8') \
        .replace('<body>', '') \
        .replace('</body>', '')


@blueprint.route('/rss')
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
    content = generate_feed(items)
    return flask.Response(content, mimetype='application/atom+xml')


def init_app(_app):
    _app.register_blueprint(blueprint, url_prefix='/contentapi')
