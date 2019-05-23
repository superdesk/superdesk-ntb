
import requests

from flask import json, current_app as app
from superdesk.signals import item_published
from superdesk.logging import logger


SCANPIX_PING_URL = 'https://api.sdl.no/v1/pushData'


def handle_item_published(sender, item, **kwargs):
    if item.get('associations'):
        for key, assoc in item['associations'].items():
            if assoc is not None and assoc.get('fetch_endpoint') == 'scanpix':
                requests.post(
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
                )
                logger.info('scanpix image published image=%s article=%s',
                            assoc.get('guid', ''),
                            item.get('guid', ''))


def init_app(app):
    if app.config.get('SCANPIX_PING_OWNER'):
        item_published.connect(handle_item_published)
        logger.info('SCANPIX ping owner configured %s', app.config['SCANPIX_PING_OWNER'])
    else:
        logger.info('SCANPIX ping owner not set')
