# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from lxml import etree
from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers.afp_newsml_1_2 import AFPNewsMLOneFeedParser
from .utils import ingest_category_from_subject, filter_missing_subjects, set_default_service


class NTBAFPNewsMLParser(AFPNewsMLOneFeedParser):

    NAME = 'ntbafpnewsml'
    label = 'NTB AFP NewsML Parser'

    def parse(self, xml, provider=None):
        item = super().parse(xml, provider)
        item['slugline'] = ''
        category = ingest_category_from_subject(item.get('subject'))  # check for sports using all ingested subjects
        item['subject'] = filter_missing_subjects(item.get('subject'))
        item['subject'].append(category)

        urgency = item.get('urgency', None)
        if urgency == 2:
            item['urgency'] = 3
        elif urgency == 4:
            item['urgency'] = 5

        set_default_service(item)

        if not item.get('headline') and item.get('body_html'):
            first_line = item.get('body_html').strip().split('\n')[0]
            item['headline'] = etree.fromstring(first_line).text.strip()

        return item


register_feed_parser(NTBAFPNewsMLParser.NAME, NTBAFPNewsMLParser())
