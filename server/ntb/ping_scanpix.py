
import requests
import mimetypes
import superdesk

from flask import json, current_app as app
from superdesk.signals import item_publish


SCANPIX_PING_URL = 'https://api.sdl.no/v1/pushData'
SCANPIX_DOWNLOAD_URL = 'https://api.scanpix.no/v2/download/quiet/{}/{}/high'

PING_TIMEOUT = 5
DOWNLOAD_TIMEOUT = (5, 25)

http = requests.Session()


def fetch_original(item):
    if item.get('renditions', {}).get('original'):
        return
    extra = item.get('extra', {})
    item.setdefault('renditions', {})
    media = app.media.get(item['_id'], 'upload')
    if not media:
        url = SCANPIX_DOWNLOAD_URL.format(extra['main_group'], item['_id'])
        provider = superdesk.get_resource_service('search_providers').find_one(req=None, _id=item['ingest_provider'])
        res = http.get(url,
                       auth=(provider['config']['username'], provider['config']['password']),
                       timeout=DOWNLOAD_TIMEOUT)
        res.raise_for_status()
        try:
            content_type = mimetypes.guess_type(extra['filename'])[0]
        except (KeyError, TypeError):
            content_type = 'image/jpeg'
        media_id = app.media.put(res.content, filename=extra.get('filename'),
                                 content_type=content_type, _id=item['_id'])
        item['renditions']['original'] = {
            'href': app.media.url_for_media(media_id),
            'width': int(extra['width']) if extra.get('width') else None,
            'height': int(extra['height']) if extra.get('height') else None,
            'mimetype': content_type,
        }


def ping_scanpix(assoc, item):
    if not app.config.get('SCANPIX_PING_OWNER'):
        return
    http.post(
        SCANPIX_PING_URL,
        json.dumps({
            'type': 'articleUsage',
            'data': {
                'owner': app.config.get('SCANPIX_PING_OWNER'),
                'media_id': assoc.get('guid', assoc.get('_id')),
                'article_id': item.get('guid', item.get('_id')),
            },
        }),
        headers={'content-type': 'application/json'},
        timeout=PING_TIMEOUT,
    )


def publish_scanpix(sender, item, **kwargs):
    if item.get('associations'):
        for key, assoc in item['associations'].items():
            if assoc is not None and assoc.get('fetch_endpoint') == 'scanpix':
                fetch_original(assoc)
                ping_scanpix(assoc, item)


def init_app(_app):
    item_publish.connect(publish_scanpix)
