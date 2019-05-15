# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import sys
from unittest import mock, skipIf
from superdesk.tests import TestCase
from ntb.io.feeding_services import newsworthy

PROVIDER = {
    "_id": "test_provider",
    "config": {
        "username": "user",
        "password": "password",
        "feed_parser": "ninjs",
        "field_aliases": []
    },
}


class NewsworthyTestCase(TestCase):

    def setUp(self):
        self.data = {
            "data": {
                "uri": "/sv/api/ninjs/newslead/21124/",
                "headline": "Ett bolag i konkurs i \u00c5l",
                "place": [{"name": "\u00c5l kommune", "code": "\u00c5l"}],
                "pubstatus": "usable",
                "renditions": {},
                "subject": [{"name": "F\u00f6retagskonkurser", "code": "norway-brreg-liquidations"}],
                "versioncreated": "2019-03-12T12:10:52Z",
                "type": "text",
                "body_html": (
                    '<p>Under förra veckan öppnades ett företagskonkurser i Ål. </p>Bolaget heter [object Object].<fig'
                    'ure><figcaption>Konkursöppningar i Ål mellan 2019-03-04 och 2019-03-10</figcaption><table class="'
                    'table responsive"><thead><tr><th scope="col">Företag</th><th scope="col">Antal ansatte</th><th sc'
                    'ope="col">Stiftelsedato</th><th scope="col">Kommune</th></tr></thead><tbody><tr><th scope="row">S'
                    'PORTSGUTTA AS</th><td class="value" data-title="Antal ansatte">9</td><td class="value" data-title'
                    '="Stiftelsedato">2015-09-30</td><td class="value" data-title="Kommune">Ål</td></tr></tbody></tabl'
                    'e></figure>NoneNone'),
                "organisation": [{"name": "Br\u00f8nn\u00f8ysundregistrene", "code": "norway-brreg"}],
            },
            "hook": {
                "resource": "Newslead",
                "hook_id": "d7c8a702-5ba2-47f1-b644-03978180a92e",
                "resource_id": 21124,
                "resource_url": "https://www.newsworthy.se/sv/api/ninjs/newslead/21124/",
                "event": "newsitem.published",
            },
        }
        self.provider = {
            'config': {'username': 'toto', 'password': 'pass', 'secret': 'secret'},
            '_id': '123'}
        super().setUp()

    @mock.patch.object(newsworthy, 'request')
    @mock.patch.object(newsworthy, 'superdesk')
    def test_feeding_service_auth(self, superdesk, request):
        """Check that a Newsworthy feed is correctly authenticated and set the right data in NewsworthyWebhookService"""
        service = superdesk.get_resource_service.return_value
        service.get.return_value = [self.provider]
        request.json = self.data
        request.args = {'checksum': 'b449eb093124d7aed7811d8a1d13f962'}
        request.authorization.get.side_effect = lambda k: {'username': 'toto',
                                                           'password': 'pass'}[k]

        self.assertTrue(newsworthy.NewsworthyFeedingServiceAuth().authorized([], 'newsworthy', 'POST'))
        self.assertEqual(newsworthy.NewsworthyWebhookService.requests_map, {request: [self.provider]})

    @mock.patch.object(newsworthy, 'request')
    @mock.patch.object(newsworthy, 'superdesk')
    def test_bad_password(self, superdesk, request):
        """Check that feeding service is not validating on bad password"""
        service = superdesk.get_resource_service.return_value
        service.get.return_value = [self.provider]
        request.json = self.data
        request.args = {'checksum': 'b449eb093124d7aed7811d8a1d13f962'}
        request.authorization.get.side_effect = lambda k: {'username': 'wrong',
                                                           'password': 'password'}[k]

        self.assertFalse(newsworthy.NewsworthyFeedingServiceAuth().authorized([], 'newsworthy', 'POST'))

    @skipIf(sys.version_info[:2] <= (3, 5), "Python 3.5 and below don't verify checksum")
    @mock.patch.object(newsworthy, 'request')
    @mock.patch.object(newsworthy, 'superdesk')
    def test_bad_checksum(self, superdesk, request):
        """Check that feeding service is not validating on bad checksum"""
        service = superdesk.get_resource_service.return_value
        service.get.return_value = [self.provider]
        request.json = self.data
        request.authorization.get.side_effect = lambda k: {'username': 'toto',
                                                           'password': 'pass'}[k]
        # this checksum is wrong on purpose
        request.args = {'checksum': 'd41d8cd98f00b204e9800998ecf8427e'}

        self.assertFalse(newsworthy.NewsworthyFeedingServiceAuth().authorized([], 'newsworthy', 'POST'))
