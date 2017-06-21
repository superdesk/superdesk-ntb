# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from xml.etree import ElementTree as ET
from superdesk.io.iptc import subject_codes

SUBJECT_TYPE = 'tobject.subject.type'
SUBJECT_MATTER = 'tobject.subject.matter'
SUBJECT_DETAIL = 'tobject.subject.detail'


# NTB NITF specific behaviour
# The current version change the main NITF parser
# TODO: move this to a NTB specific NITF module once SD-4650 is fixed

def build_subject(xml):
    voc_subjects_map = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='subject_custom')
    subjects = []
    qcodes = []  # we check qcodes to avoid duplicates
    for elem in xml.findall('head/tobject/tobject.subject'):
        qcode = elem.get('tobject.subject.refnum')
        if qcode in qcodes:
            # we ignore duplicates
            continue
        else:
            qcodes.append(qcode)

        name = elem.get(SUBJECT_TYPE, elem.get(SUBJECT_MATTER, elem.get(SUBJECT_DETAIL)))
        if name is None:
            name = subject_codes[qcode]
        subject = {
            'name': name,
            'qcode': qcode,
            'scheme': 'subject_custom',
        }
        try:
            voc_subject = next((s for s in voc_subjects_map['items'] if s['qcode'] == qcode))
        except StopIteration:
            parent = None
        else:
            parent = voc_subject.get('parent')
        if parent is not None:
            subject['parent'] = parent
        subjects.append(subject)
    return subjects


def build_service(elem):
    """Fill service (anpa_category for NTB) according to vocabularies"""
    category = elem.get('content')
    voc_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')['items']
    service = [{'name': elem.get('content')}]
    update = None
    for voc_category in voc_categories:
        if category == voc_category['name']:
            try:
                update = {'qcode': voc_category['qcode'], 'language': voc_category['language']}
            except KeyError:
                continue
            else:
                break
    if update is not None:
        service[0].update(update)
    else:
        service[0]['qcode'] = elem.get('content')
    return service


def build_body_html(xml):
    elements = []
    for elem in xml.find('body/body.content'):
        if elem.tag == 'p' and elem.get('class') == 'lead':
            continue
        elements.append(ET.tostring(elem, encoding='unicode'))
    return ''.join(elements)


NITF_MAPPING = {
    'anpa_category': {'xpath': "head/meta[@name='NTBTjeneste']",
                      'filter': build_service,
                      },
    'priority': {'update': True,
                 'xpath': "head/meta[@name='NTBPrioritet']"},
    'ntb_category': {'xpath': 'head/tobject[@tobject.type]',
                     'filter': lambda e: [{'qcode': e.get('tobject.type'),
                                           'name': e.get('tobject.type'),
                                           'scheme': 'category'}],
                     # category is stored in subject for NITF, so we need a key_hook
                     'key_hook': lambda item, value: item.setdefault('subject', []).extend(value)},
    'genre': {'xpath': 'head/tobject[@tobject.type]/tobject.property[@tobject.property.type]',
                       'filter': lambda e: [{'qcode': e.get('tobject.property.type'),
                                             'name': e.get('tobject.property.type'),
                                             'scheme': 'genre_custom'}]},
    'subject': {'callback': build_subject,
                # subject is also used by categories, so we need a key_hook
                'key_hook': lambda item, value: item.setdefault('subject', []).extend(value)},
    'body_html': build_body_html,
    'slugline': 'head/docdata/du-key/@key',
    'abstract': "body/body.content/p[@class='lead']",
    'keywords': '',  # keywords are ignored on purpose
}
