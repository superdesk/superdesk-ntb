
import requests
import mimetypes
import superdesk

from flask import json, current_app as app
from superdesk.signals import item_published
from superdesk.logging import logger


SCANPIX_PING_URL = 'https://api.sdl.no/v1/pushData'
SCANPIX_DOWNLOAD_URL = 'https://api.scanpix.no/v2/download/quiet/{}/{}/high'

PING_TIMEOUT = 5
DOWNLOAD_TIMEOUT = (5, 25)

http = requests.Session()


def fetch_original(item):
    try:
        if item.get('renditions', {}).get('original'):
            return
        extra = item.get('extra', {})
        item.setdefault('renditions', {})
        media = app.media.get(item['_id'], 'upload')
        if not media:
            url = SCANPIX_DOWNLOAD_URL.format(extra['main_group'], item['_id'])
            provider = superdesk.get_resource_service('search_providers') \
                .find_one(req=None, _id=item['ingest_provider'])
            res = http.get(
                url,
                auth=(provider['config']['username'], provider['config']['password']),
                timeout=DOWNLOAD_TIMEOUT)
            res.raise_for_status()
            try:
                content_type = mimetypes.guess_type(extra['filename'])[0]
            except (KeyError, TypeError):
                content_type = 'image/jpeg'
            media_id = app.media.put(
                res.content,
                filename=extra.get('filename'),
                content_type=content_type, _id=item['_id'])
            item['renditions']['original'] = {
                'href': app.media.url_for_media(media_id),
                'width': int(extra['width']) if extra.get('width') else None,
                'height': int(extra['height']) if extra.get('height') else None,
                'mimetype': content_type,
            }
    except Exception as e:
        logger.exception(e)


def ping_scanpix(assoc, item):
    for key in ['OWNER', 'USERNAME', 'PASSWORD']:
        if not app.config.get('SCANPIX_PING_%s' % key):
            return
    try:
        res = requests.post(
            SCANPIX_PING_URL,
            json.dumps({
                'type': 'articleUsage',
                'data': {
                    'owner': app.config['SCANPIX_PING_OWNER'],
                    'media_id': assoc.get('guid', assoc.get('_id')),
                    'article_id': item.get('guid', item.get('_id')),
                },
            }),
            headers={'content-type': 'application/json'},
            auth=(app.config['SCANPIX_PING_USERNAME'], app.config['SCANPIX_PING_PASSWORD']),
        )
        logger.info('scanpix image published status=%d image=%s article=%s',
                    res.status_code,
                    assoc.get('guid', ''),
                    item.get('guid', ''))
    except Exception as e:
        logger.exception(e)


def publish_scanpix(sender, item, **kwargs):
    if item.get('associations'):
        for key, assoc in item['associations'].items():
            if assoc is not None and assoc.get('fetch_endpoint') == 'scanpix':
                # fetch_original(assoc)  #  not yet
                ping_scanpix(assoc, item)


def init_app(app):
    item_published.connect(publish_scanpix)
    if app.config.get('SCANPIX_PING_OWNER') and app.config.get('SCANPIX_PING_USERNAME'):
        logger.info('SCANPIX ping owner configured %s', app.config['SCANPIX_PING_OWNER'])
    else:
        logger.info('SCANPIX ping owner not set')
