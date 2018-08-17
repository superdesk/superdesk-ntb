"""
    This macro doesn't change any content, but when executed it'll
    transfer the article to the nynorsk-API. There it will be stored
    and used for later improvements of the translation software.
"""

import requests
from requests.auth import HTTPBasicAuth


def nob_NO_publish_macro(item, **kwargs):
    creds = HTTPBasicAuth('superdesk', 'babel')
    #payload = {k: item.get(k) for k in item if k in ('guid', 'headline', 'body_html', 'body_text', 'abstract', 'description_html', 'description_text')}
    payload=item
    requests.post('http://api.smalldata.no:8080/publish', data=payload, timeout=(10, 30), auth=creds)
    return item


name = 'Bokmal to Nynorsk Publish Macro'
label = 'Språkvask - Lagre'
callback = nob_NO_publish_macro
access_type = 'frontend'
action_type = 'direct'
