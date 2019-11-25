# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish.publish_service import PublishService
from .ntb_nitf import NTBNITFFormatter


class NTBNITFMultiServiceFormatter(NTBNITFFormatter):
    """This NITF formatter generates single file with all services."""

    FORMAT_TYPE = 'ntbnitf'  # default ntb nitf formatter

    def _format_service(self, article):
        try:
            service_names = ", ".join(service.get("name", "") for service in article['anpa_category'])
            return service_names
        except (KeyError):
            pass


class NTBNITFMultiServiceMediaFormatter(NTBNITFMultiServiceFormatter):

    FORMAT_TYPE = 'ntbnitfmedia'

    def _get_media_source(self, data):
        if data.get('type') == 'picture':
            return self._get_original_href(data)
        return super()._get_media_source(data)


PublishService.register_file_extension(NTBNITFMultiServiceFormatter.FORMAT_TYPE, 'xml')
PublishService.register_file_extension(NTBNITFMultiServiceMediaFormatter.FORMAT_TYPE, 'xml')
