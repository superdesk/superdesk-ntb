# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.registry import register_feed_parser
from superdesk.io.feed_parsers.newsml_2_0 import NewsMLTwoFeedParser
from .utils import ingest_category_from_subject, filter_missing_subjects, set_default_service


class NTBNewsMLTwoFeedParser(NewsMLTwoFeedParser):

    NAME = 'ntbnewsml2'
    label = 'NTB NewsML-G2 Parser'

    def parse(self, xml, provider=None):
        items = super().parse(xml, provider)
        for item in items:
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
        return items


register_feed_parser(NTBNewsMLTwoFeedParser.NAME, NTBNewsMLTwoFeedParser())
