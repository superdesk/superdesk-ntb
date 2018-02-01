# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.feed_parsers.ritzau import RitzauFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError
from . import utils


class RitzauFeedParser(RitzauFeedParser):
    """
    Feed Parser which can parse Ritzau XML feed
    """
    _subjects_map = None

    NAME = 'ntb_ritzau'
    label = "NTB Ritzau feed"

    def parse(self, xml, provider=None):
        item = super().parse(xml, provider)
        try:
            category = utils.ingest_category_from_subject(item.get('subject'))
            item.setdefault('subject', []).append(category)
            utils.set_default_service(item)
        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)
        return item


register_feed_parser(RitzauFeedParser.NAME, RitzauFeedParser())
