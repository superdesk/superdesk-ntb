"""
    nb-NO to nn-NO Metadata Macro will perform the following changes to current content item:
    - change the language to nn-NO
    - change the body footer to "(©NPK)" - NB: copyrightsign, not @
    - change the service (ANPA category) to "NPKTema"
"""

import requests
import logging
from requests.auth import HTTPBasicAuth

def nb_NO_to_nn_NO_metadata_macro(item, **kwargs):
    item['body_footer'] = '(©NPK)'
    item['language'] = 'nn-NO'
    item['anpa_category'] = [
        {
            'qcode': 'a',
            'single_value': True,
            'name': 'NPKTema',
            'language': 'nn-NO',
            'scheme': None
        }
    ]
    """
    Translation start
    """
    logger = logging.getLogger('superdesk')
    payload = {k: item.get(k) for k in item if k in ('guid', 'evolvedfrom', 'versioncreated', 'headline', 'description_text', 'description_html', 'body_text', 'body_html')}
    logger.debug('Starting request')
    r = requests.post('http://api.smalldata.no:8080/translate', data=payload, timeout=(10, 30), auth=HTTPBasicAuth('superdesk', 'babel'))
    logger.debug('Request done')
    if r.status_code == 200:
        logger.warning('200 Success')
        item.update(r.json())
    else:
        logger.warning('Something went wrong')
    """
        Translation end
    """
    return item

name = 'Bokmal to Nynorsk Metadata Macro'
label = 'Translate to Nynorsk Macro'
callback = nb_NO_to_nn_NO_metadata_macro
access_type = 'backend'
action_type = 'direct'
from_languages = ['nb-NO']
to_languages = ['nn-NO']
