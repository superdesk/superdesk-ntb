"""
    nb-NO to nn-NO Metadata Macro will perform the following changes to current content item:
    - change the language to nn-NO
"""

import requests
from requests.auth import HTTPBasicAuth


def nob_NO_translate_macro(item, **kwargs):    
    creds = HTTPBasicAuth('superdesk', 'babel')
    r = requests.post('http://api.smalldata.no:8080/translate', data=item, timeout=(10, 30), auth=creds)
    if r.status_code == 200:
        item.update(r.json())
    return item


name = 'Bokmal to Nynorsk Translate Macro'
label = 'Omsett NB til NN'
callback = nob_NO_translate_macro
access_type = 'frontend'
action_type = 'direct'
from_languages = ['nb-NO']
to_languages = ['nn-NO']
