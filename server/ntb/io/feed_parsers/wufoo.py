#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.feed_parsers import FeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.io.commands.update_ingest import LAST_INGESTED_ID
from datetime import datetime, date
from superdesk.utc import local_to_utc
import html
import requests
import logging

logger = logging.getLogger(__name__)

# wufoo inputs expect Pactific Time Zone,
# really not handy but we have to deal with it
# PTZ = timezone('America/Los_Angeles')

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = DATE_FORMAT + " %H:%M:%S"
FORM_HASH = "q1hpdwg91h6ubl1"
TIMEZONE = 'Europe/Oslo'  # timezone is actually user timezone, so we're guessing here

FIELDS_MAP = {
    "author": "Field1",
    "permission": "Field2",
    "name": "Field102",
    "birth place": "Field103",
    "birth date": "Field104",
    "title": "Field105",
    "address": "Field113",
    "address_2": "Field114",
    "city": "Field115",
    "state": "Field116",
    "zip": "Field117",
    "country": "Field118",
    "email": "Field111",
    "phone": "Field112",
    "further sources": "Field120",
    "biography": "Field119",
    "photo": "Field121",
}

NO_MONTHS = [
    "januar",
    "februar",
    "mars",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "desember",
]


class WufooArticle(dict):
    """A dictionnary which map fields name to their ID automatically"""

    def __getitem__(self, key):
        if key in FIELDS_MAP:
            key = FIELDS_MAP[key]
        try:
            return super().__getitem__(key)
        except KeyError:
            # we don't want the form to fail if a field is missing
            return ""


class WufooFeedParser(FeedParser):

    NAME = "wufoo"

    def can_parse(self, article):
        # parse is called directly by wufoo feeding service, and we don't want the parser to
        # be used with any other feeding service, so we return False
        return False

    def strftime(self, _date, _format):
        """Convert date to string according to format

        :param date _date: date to convert
        :param str _format: format to use (same as for datetime.strftime)
        :return str: converted date
        """
        _datetime = datetime.combine(_date, datetime.min.time())
        return _datetime.strftime(_format)

    def parse(self, wufoo_data, provider=None):
        if provider is None:
            return
        url = wufoo_data["url"]
        user = wufoo_data["user"]
        api_key = wufoo_data["api_key"]
        query = wufoo_data["form_query_entries_tpl"].format(form_hash=FORM_HASH)
        update = wufoo_data["update"]
        last_ingested_id = provider.get(LAST_INGESTED_ID)
        auth = (api_key, "")
        params = {"pageSize": 100}
        if last_ingested_id is not None:
            params["Filter1"] = "EntryId Is_greater_than " + last_ingested_id

        r = requests.get(url + query, params=params, auth=auth)
        items = []
        for entry in r.json()["Entries"]:
            entry["uid_prefix"] = "wufoo_{}_{}_".format(user, FORM_HASH)
            try:
                items.append(self.parse_article(entry))
            except Exception as e:
                logger.error(u"Can't parse Wufoo submission {id}: {reason}".format(id=entry["EntryId"], reason=e))
            update["last_ingested_id"] = entry["EntryId"]

        return items

    def parse_article(self, article):
        article = WufooArticle(article)
        item = {"byline": "NTB"}
        item["guid"] = article["uid_prefix"] + article["EntryId"]
        today = date.today()
        try:
            birth_date = datetime.strptime(article["birth date"], DATE_FORMAT).date()
        except ValueError as e:
            birth_date = today
            logger.warning("birth date has invalid format: {msg}".format(msg=e))
        age = int((today - birth_date).days / 365.25)
        jubilee_date = birth_date.replace(year=today.year)
        if jubilee_date < today:
            jubilee_date = jubilee_date.replace(year=jubilee_date.year + 1)
        address = "\n".join(article[k] for k in ("address", "address_2") if article[k])
        try:
            photo_url = article["photo"].split()[1][1:-1]
            if not photo_url.startswith("http"):
                logging.error(u"invalid photo format: {}".format(article["photo"]))
                raise ValueError
        except (IndexError, ValueError):
            photo_url = None

        item["headline"] = "{age} år {jubilee_date}: {title} {name}, {address}, {zip} {city}{country}".format(
            age=age + 1,
            jubilee_date=self.strftime(jubilee_date, "%d. " + NO_MONTHS[jubilee_date.month - 1]),
            title=article["title"],
            name=article["name"],
            address=address,
            zip=article["zip"],
            city=article["city"],
            country=", {}".format(article["country"]) if article["country"] not in ("Norge", "Noreg") else "",
        )
        item["slugline"] = "FØDSELSDAG-" + self.strftime(jubilee_date, "%y%m%d")
        item["anpa_category"] = [{"name": "Omtaletjenesten", "qcode": "o", "language": "nb-NO"}]
        category = "Jubilantomtaler"
        item["subject"] = [{"qcode": category, "name": category, "scheme": "category"}]
        genre = "Nyheter"
        item["genre"] = [{"qcode": genre, "name": genre, "scheme": "genre_custom"}]
        xhtml = [html.escape(article["biography"]).replace("\n", "<br/>\n")]
        if photo_url is not None:
            label = "photo"
            xhtml.append('<a href="{url}">{label}</a>'.format(url=html.escape(photo_url), label=label))
        item["body_html"] = "<p>{}</p>".format("\n<br/>\n".join(xhtml))
        item["ednote"] = (
            "Kilder: \n"
            + article["further sources"]
            + "\n\n"
            + "Fødested: {}\n".format(article["birth place"])
            + "Sendt inn av: {}\n".format(article["author"])
            + "Godkjent: {}\n".format("Ja" if article["permission"] else "Nei")
            + "Epost: {}\n".format(article["email"])
            + "Tlf: {}"
        ).format(article["phone"])
        try:
            item["versioncreated"] = self._parse_date(article["DateCreated"])
            item["firstcreated"] = item["versioncreated"]
        except ValueError as e:
            logger.warning("DateCreated has invalid format: {msg}".format(msg=e))

        item["sign_off"] = "personalia@ntb.no"
        return item

    def _parse_date(self, value):
        dt = datetime.strptime(value, DATETIME_FORMAT)
        return local_to_utc(TIMEZONE, dt)


register_feed_parser(WufooFeedParser.NAME, WufooFeedParser())
