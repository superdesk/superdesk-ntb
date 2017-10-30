# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from ntb.publish.ntb_nitf import NTBNITFFormatter
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.publish.publish_service import PublishService


class NTBNITFLegacyFormatter(NTBNITFFormatter):
    def can_format(self, format_type, article):
        """
        Method check if the article can be formatted to NTB NIT Legacy.

        :param str format_type:
        :param dict article:
        :return: True if article can formatted else False
        """
        return format_type == 'ntbnitflegacy' and article[ITEM_TYPE] == CONTENT_TYPE.TEXT

    def format(self, original_article, subscriber, codes=None, encoding="us-ascii"):
        """For every service create a article nitf format."""
        if len(original_article.get('anpa_category', [])) <= 1:
            return super().format(original_article, subscriber, codes, encoding)

        article = original_article.copy()
        articles = []

        for service in original_article['anpa_category']:
            article['anpa_category'] = [service]
            articles += super().format(article, subscriber, codes, encoding)

        return articles


PublishService.register_file_extension('ntbnitflegacy', 'xml')
