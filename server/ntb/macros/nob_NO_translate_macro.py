"""
    nb-NO to nn-NO Metadata Macro will perform the following changes to current content item:
    - change the language to nn-NO
"""

import requests
from requests.auth import HTTPBasicAuth

def nob_NO_translate_macro(item, **kwargs):
    """
    Translation start
    """
    #payload = {k: item.get(k) for k in item if k in ('guid', 'evolvedfrom', 'versioncreated', 'abstract', 'headline', 'description_text', 'description_html', 'body_text', 'body_html')}
    payload = item
    r = requests.post('http://api.smalldata.no:8080/translate', data=payload, timeout=(10, 30), auth=HTTPBasicAuth('superdesk', 'babel'))
    if r.status_code == 200:
        item.update(r.json())
    """
        Translation end
    """
    return item

name = 'Bokmal to Nynorsk Translate Macro'
label = 'Omsett NB til NN'
callback = nob_NO_translate_macro
access_type = 'frontend'
action_type = 'direct'
from_languages = ['nb-NO']
to_languages = ['nn-NO']
