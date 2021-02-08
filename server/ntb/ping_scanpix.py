
import hashlib
import requests
import mimetypes
import superdesk

from flask import json, current_app as app
from superdesk.signals import item_publish
from superdesk.logging import logger


SCANPIX_PING_URL = 'https://api.sdl.no/v1/pushData'
SCANPIX_DOWNLOAD_URL = 'https://api.scanpix.no/v2/download/quiet/{}/{}/high'

PING_TIMEOUT = (5, 5)
DOWNLOAD_TIMEOUT = (5, 25)
MEDIA_RESOURCE = 'upload'

http = requests.Session()


def fetch_original(item):
    try:
        if item.get('renditions', {}).get('original'):
            return
        extra = item.get('extra', {})
        item.setdefault('renditions', {})
        media_id = hashlib.sha1(item['guid'].encode()).hexdigest()
        media = app.media.get(media_id, MEDIA_RESOURCE)
        if not media:
            url = SCANPIX_DOWNLOAD_URL.format(extra['main_group'], item['guid'])
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
            app.media.put(
                res.content,
                filename=extra.get('filename'),
                content_type=content_type,
                _id=media_id)
            media = app.media.get(media_id, MEDIA_RESOURCE)
        item['renditions']['original'] = {
            'href': app.media.url_for_media(media._id, media.content_type),
            'width': int(extra['width']) if extra.get('width') else None,
            'height': int(extra['height']) if extra.get('height') else None,
            'mimetype': media.content_type,
        }
    except Exception as e:
        logger.exception(e)


def ping_scanpix(assoc, item):
    for key in ['OWNER', 'USERNAME', 'PASSWORD']:
        if not app.config.get('SCANPIX_PING_%s' % key):
            return
    try:
        res = http.post(
            SCANPIX_PING_URL,
            json.dumps({
                'type': 'articleUsage',
                'data': {
                    'owner': app.config['SCANPIX_PING_OWNER'],
                    'media_id': assoc.get('guid', assoc.get('_id')),
                    'article_id': item.get('guid', item.get('_id')),
                    'services': [cat.get('name') for cat in item.get('anpa_category', [])],
                },
            }),
            headers={'content-type': 'application/json'},
            auth=(app.config['SCANPIX_PING_USERNAME'], app.config['SCANPIX_PING_PASSWORD']),
            timeout=PING_TIMEOUT,
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
                if assoc.get('type') == 'picture':
                    fetch_original(assoc)
                ping_scanpix(assoc, item)


def init_app(app):
    item_publish.connect(publish_scanpix)
    if app.config.get('SCANPIX_PING_OWNER') and app.config.get('SCANPIX_PING_USERNAME'):
        logger.info('SCANPIX ping owner configured %s', app.config['SCANPIX_PING_OWNER'])
    else:
        logger.info('SCANPIX ping owner not set')
