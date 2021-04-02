# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import re
import pytz
import logging
import superdesk

from lxml import etree
from copy import deepcopy
from datetime import datetime
from flask import current_app as app

from superdesk import etree as sd_etree, get_resource_service
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.publish.formatters.nitf_formatter import NITFFormatter, EraseElement
from superdesk.publish.publish_service import PublishService
from superdesk.errors import FormatterError

logger = logging.getLogger(__name__)
tz = None

EMBED_RE = re.compile(r"<!-- EMBED START ([a-zA-Z]+ {id: \"(?P<id>.+?)\"}) -->.*"
                      r"<!-- EMBED END \1 -->", re.DOTALL)
FILENAME_FORBIDDEN_RE = re.compile(r"[^a-zA-Z0-9._-]")
STRIP_INVALID_CHARS_RE = re.compile('[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
ENCODING = 'iso-8859-1'
LANGUAGE = 'nb-NO'  # default language for ntb
assert ENCODING != 'unicode'  # use e.g. utf-8 for unicode


def _get_rewrite_sequence(article):
    return int(article.get('rewrite_sequence') or 0)


def _get_language(article):
    return article.get('language') or LANGUAGE


def get_content_field(article, field):
    content_type = get_resource_service("content_types").find_one(req=None, _id=article['profile'])
    if not content_type:
        return
    return content_type.get("schema", {}).get(field)


class NTBNITFFormatter(NITFFormatter):
    """This is NITF formatter 1.0 generating single file with first service only."""

    XML_DECLARATION = '<?xml version="1.0" encoding="iso-8859-1" standalone="yes"?>'
    FORMAT_TYPE = 'ntbnitf10'

    def __init__(self):
        NITFFormatter.__init__(self)
        self.HTML2NITF['p']['filter'] = self.p_filter

    def can_format(self, format_type, article):
        """
        Method check if the article can be formatted to NTB NIT
        :param str format_type:
        :param dict article:
        :return: True if article can formatted else False
        """
        return format_type == self.FORMAT_TYPE and article[ITEM_TYPE] == CONTENT_TYPE.TEXT

    def strip_invalid_chars(self, string):
        if string is None:
            string = ''
        return STRIP_INVALID_CHARS_RE.sub('', string)

    def format(self, original_article, subscriber, codes=None, encoding="us-ascii"):
        article = deepcopy(original_article)
        self._populate_metadata(article)
        global tz
        if tz is None:
            # first time this method is launched
            # we set timezone and NTB specific filter
            tz = pytz.timezone(superdesk.app.config['DEFAULT_TIMEZONE'])
        try:
            if article.get('body_html'):
                article['body_html'] = article['body_html'].replace('<br>', '<br />')
            pub_seq_num = get_resource_service('subscribers').generate_sequence_number(subscriber)
            nitf = self.get_nitf(article, subscriber, pub_seq_num)
            try:
                nitf.attrib['baselang'] = _get_language(article)
            except KeyError:
                pass

            encoded = etree.tostring(nitf, encoding=ENCODING, xml_declaration=False, pretty_print=True)

            return [{'published_seq_num': pub_seq_num,
                     # formatted_item can be used for preview, so we keep unicode version there
                     'formatted_item': self.XML_DECLARATION + '\n' + etree.tostring(nitf, encoding="unicode"),
                     'encoded_item': (self.XML_DECLARATION + '\n').encode(ENCODING) + encoded}]
        except Exception as ex:
            app.sentry.captureException()
            raise FormatterError.nitfFormatterError(ex, subscriber)

    def _populate_metadata(self, article):
        """
        For tree type vocabularies add the parent if a child is present
        """
        vocabularies = list(get_resource_service('vocabularies').get(None, None))
        fields = {'place': 'place_custom', 'subject': 'subject_custom'}
        for field in fields:
            vocabulary = self._get_list_element(vocabularies, '_id', fields[field])
            if not vocabulary:
                continue
            vocabulary_items = vocabulary.get('items', [])
            field_values = article.get(field, [])
            for value in list(field_values):
                if not value.get('parent', None):
                    continue
                parent = self._get_list_element(field_values, 'qcode', value['parent'])
                if not parent:
                    parent = self._get_list_element(vocabulary_items, 'qcode', value['parent'])
                    parent['scheme'] = fields[field]
                    field_values.append(parent)

    def _get_list_element(self, items, key, value):
        """
        Get the element from the list by field 'key' and value 'value'
        """
        for item in items:
            if item.get(key, None) == value:
                return item
        return None

    def p_filter(self, root_elem, p_elem):
        """Modify p element to have 'txt' or 'txt-ind' attribute
        'txt' is only used immediatly after "hl2" elem, txt-ind in all other cases
        """
        if p_elem.get('class') == 'ntb-media':
            raise EraseElement("Element need to be erased")
        parent = p_elem.find('..')
        children = list(parent)
        idx = children.index(p_elem)
        if idx > 0 and children[idx - 1].tag == "hl2" or p_elem.attrib.get('class', None) == 'footer-txt':
            p_elem.attrib['class'] = 'txt'
        else:
            p_elem.attrib['class'] = 'txt-ind'

    def _get_ntb_category(self, article):
        for s in article.get('subject', []):
            if s.get('scheme') == 'category':
                return s['qcode']
        return ''

    def _get_ntb_subject(self, article):
        update = _get_rewrite_sequence(article)
        subject_prefix = "ny{}-".format(update) if update else ""
        return subject_prefix + self._get_ntb_slugline(article)

    def _get_ntb_slugline(self, article):
        slugline = article.get('slugline', '')
        slugline = re.sub(r'[^a-zA-Z0-9ÆØÅæøå\.\- ]', "-", slugline)
        return slugline

    def _format_tobject(self, article, head):
        return etree.SubElement(head, 'tobject', {'tobject.type': self._get_ntb_category(article)})

    def _format_docdata_dateissue(self, article, docdata):
        etree.SubElement(
            docdata,
            'date.issue',
            attrib={'norm': article['versioncreated'].astimezone(tz).strftime("%Y-%m-%dT%H:%M:%S")})

    def _format_docdata_doc_id(self, article, docdata):
        doc_id = "NTB{family_id}_{version:02}".format(
            family_id=article['family_id'],
            version=_get_rewrite_sequence(article))
        etree.SubElement(docdata, 'doc-id', attrib={'regsrc': 'NTB', 'id-string': doc_id})

    def _format_date_expire(self, article, docdata):
        pass

    def _format_docdata(self, article, docdata):
        super()._format_docdata(article, docdata)
        state_prov = "name"
        county_dist = "qcode"

        if "slugline" in article:
            key_list = etree.SubElement(docdata, "key-list")
            etree.SubElement(
                key_list, "keyword", attrib={"key": self._get_ntb_slugline(article)}
            )
            etree.SubElement(
                docdata,
                "du-key",
                attrib={
                    "version": str(_get_rewrite_sequence(article) + 1),
                    "key": self._get_ntb_slugline(article),
                },
            )

        if article.get("profile") and get_content_field(article, "place"):
            places = [place for place in article.get("place", []) if place.get("scheme") == "place_custom"]
            state_prov = "ntb_parent"
            county_dist = "ntb_qcode"
        else:
            places = [place for place in article.get("place", []) if place.get("source") == "imatrics"]

        for place in places:
            evloc = etree.SubElement(docdata, "evloc")
            for key, att in ((state_prov, "state-prov"), (county_dist, "county-dist")):
                try:
                    value = place[key]
                except KeyError:
                    pass
                else:
                    if value is not None:
                        evloc.attrib[att] = value

    def _format_pubdata(self, article, head):
        pub_date = article['versioncreated'].astimezone(tz).strftime("%Y%m%dT%H%M%S")
        pubdata = etree.SubElement(head, 'pubdata', attrib={'date.publication': pub_date})
        article['pubdata'] = pubdata  # needed to access pubdata when formatting body content

    def _format_subjects(self, article, tobject):
        if article.get("profile"):
            content_type = get_content_field(article, "subject")
            if (content_type and "subject_custom" in content_type.get("schema")["schema"]["scheme"]["allowed"]):
                subjects = [
                    s
                    for s in article.get("subject", [])
                    if s.get("scheme") == "subject_custom"
                ]
                for subject in subjects:
                    name_key = (
                        "tobject.subject.matter"
                        if subject.get("parent")
                        else "tobject.subject.type"
                    )
                    etree.SubElement(
                        tobject,
                        "tobject.subject",
                        {
                            "tobject.subject.refnum": subject.get("qcode", ""),
                            name_key: subject.get("name", ""),
                        },
                    )
            else:
                topics = [
                    s
                    for s in article.get("subject", [])
                    if s.get("scheme") == "topics" and s.get("source") == "imatrics"
                ]
                for topic in topics:
                    name_key = (
                        "tobject.subject.matter"
                        if topic.get("name")
                        else "tobject.subject.type"
                    )
                    etree.SubElement(
                        tobject,
                        "tobject.subject",
                        {
                            "tobject.subject.refnum": topic.get("altids", {}).get(
                                "medtop"
                            ),
                            name_key: topic.get("name", ""),
                        },
                    )

    def _format_datetimes(self, article, head):
        created = article['versioncreated'].astimezone(tz)
        etree.SubElement(head, 'meta', {'name': 'timestamp', 'content': created.strftime("%Y.%m.%d %H:%M:%S")})
        etree.SubElement(head, 'meta', {'name': 'ntb-dato', 'content': created.strftime("%d.%m.%Y %H:%M")})
        etree.SubElement(head, 'meta', {'name': 'NTBUtDato', 'content': created.strftime("%d.%m.%Y")})

    def _get_filename(self, article):
        """Return filename as specified by NTB
        filename pattern: date_time_service_category_subject.xml
        example: 2016-08-16_11-07-46_Nyhetstjenesten_Innenriks_ny1-rygge-nedgang.xml
        """
        metadata = {}
        metadata['date'] = article['versioncreated'].astimezone(tz).strftime("%Y-%m-%d_%H-%M-%S")
        try:
            metadata['service'] = article['anpa_category'][0]['name']
        except (KeyError, IndexError):
            metadata['service'] = ""
        metadata['category'] = self._get_ntb_category(article)
        metadata['subject'] = self._get_ntb_subject(article)
        filename_raw = "{date}_{service}_{category}_{subject}.{ext}".format(
            ext="xml",
            **metadata)
        return FILENAME_FORBIDDEN_RE.sub('-', filename_raw)

    def _format_meta_priority(self, article, head):
        priority = article.get('priority')
        if priority is not None:
            etree.SubElement(head, 'meta', {'name': 'NTBNewsValue', 'content': str(priority)})

    def _format_meta(self, article, head, destination, pub_seq_num):
        super()._format_meta(article, head, destination, pub_seq_num)
        article['head'] = head  # needed to access head when formatting body content
        etree.SubElement(head, 'meta', {'name': 'NTBEditor', 'content': 'Superdesk'})

        service = self._format_service(article)
        if service:
            etree.SubElement(head, 'meta', {'name': 'NTBTjeneste', 'content': service})

        etree.SubElement(head, 'meta', {'name': 'filename', 'content': self._get_filename(article)})

        self._format_datetimes(article, head)
        if 'slugline' in article:
            etree.SubElement(head, 'meta', {'name': 'NTBStikkord', 'content': self._get_ntb_slugline(article)})
        etree.SubElement(head, 'meta', {'name': 'subject', 'content': self._get_ntb_subject(article)})

        etree.SubElement(head, 'meta', {'name': 'NTBID', 'content': 'NTB{}'.format(article['family_id'])})

        # these static values never change
        etree.SubElement(head, 'meta', {'name': 'NTBDistribusjonsKode', 'content': 'ALL'})
        etree.SubElement(head, 'meta', {'name': 'NTBKanal', 'content': 'A'})

        # daily counter
        day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        pub_queue = get_resource_service("publish_queue")
        daily_count = pub_queue.find({'transmit_started_at': {'$gte': day_start}}).count() + 1
        etree.SubElement(head, 'meta', {'name': 'NTBIPTCSequence', 'content': str(daily_count)})

        # name
        try:
            name = article['extra']['ntb_pub_name']
        except KeyError:
            pass
        else:
            etree.SubElement(head, 'meta', {'name': 'NTBKilde', 'content': name})

    def _format_service(self, article):
        try:
            return article['anpa_category'][0].get('name')
        except (KeyError, IndexError):
            pass

    def _format_body_head_abstract(self, article, body_head):
        # abstract is added in body_content for NTB NITF
        pass

    def _format_body_head_dateline(self, article, body_head):
        try:
            dateline_content = article['dateline']['located']['city']
        except (KeyError, TypeError):
            pass
        else:
            dateline = etree.SubElement(body_head, 'dateline')
            dateline.text = dateline_content

    def _format_body_head_distributor(self, article, body_head):
        distrib = etree.SubElement(body_head, 'distributor')
        org = etree.SubElement(distrib, 'org')
        language = _get_language(article)
        if language == 'nb-NO':
            org.text = 'NTB'
        elif language == 'nn-NO':
            org.text = 'NPK'

    def _add_media(self, body_content, type_, mime_type, source, caption, featured=None, cls=None, alternate_text=None):
        media = etree.SubElement(body_content, 'media')
        media.attrib['media-type'] = type_
        if cls:
            media.set('class', cls)
        if featured is not None:
            media.set('class', 'illustrasjonsbilde')
        media_reference = etree.SubElement(media, 'media-reference')
        if mime_type is not None:
            media_reference.set('mime-type', mime_type)
        if alternate_text is not None:
            media_reference.set('alternate-text', alternate_text)
        media_reference.set('source', source)
        media_caption = etree.SubElement(media, 'media-caption')
        media_caption.text = caption

    def _add_meta_media_counter(self, head, counter):
        # we need to add a <meta/> in header with the number of media
        # we first check index of first meta element to group them
        first_meta = head.find("meta")
        if first_meta is not None:
            index = list(head).index(first_meta)
        else:
            index = 1
        elem = etree.Element('meta', {'name': 'NTBBilderAntall', 'content': str(counter)})
        head.insert(index, elem)

    def _format_body_content(self, article, body_content):
        head = article.pop('head')

        # abstract
        if 'abstract' in article:
            p = etree.SubElement(body_content, 'p', {'lede': "true", 'class': "lead"})
            abstract = sd_etree.parse_html(article['abstract'], content='html')
            abstract_txt = etree.tostring(abstract, encoding='unicode', method='text')
            p.text = abstract_txt

        # media
        media_data = []
        try:
            associations = article['associations']
        except KeyError:
            pass
        else:
            feature_image = associations.get('featureimage')
            if feature_image is not None:
                feature_image['_featured'] = 'image'
                media_data.append(feature_image)
            else:
                feature_media = associations.get('featuremedia')
                if feature_media is not None:
                    feature_media['_featured'] = 'media'
                    media_data.append(feature_media)

        def repl_embedded(match):
            """Embedded in body_html handling"""
            # this method do 2 important things:
            # - it remove the embedded from body_html
            # - it fill media_data with embedded data in order of appearance
            id_ = match.group("id")
            try:
                data = associations[id_]
            except KeyError:
                logger.warning("Expected association {} not found!".format(id_))
            else:
                if data is None:
                    logger.warning("media data for association {} is empty, ignoring!".format(id_))
                else:
                    media_data.append(data)
            return ''

        html = self.strip_invalid_chars(EMBED_RE.sub(repl_embedded, article.get('body_html') or ''))
        # it is a request from SDNTB-388 to use normal space instead of non breaking spaces
        # so we do this replace
        html = html.replace('&nbsp;', ' ')

        # at this point we have media data filled in right order
        # and no more embedded in html

        # regular content
        # we use XMLParser instead of HTMLParser here because HTMLParser will not remove all whitespace
        # resulting in trouble when pretty printing
        # (cf. http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output)
        parser = etree.XMLParser(recover=True, remove_blank_text=True)
        try:
            html_elts = etree.fromstring(''.join(('<div>', html, '</div>')), parser)
        except Exception as e:
            raise ValueError(u"Can't parse body_html content: {}".format(e))

        # <p class="lead" lede="true"> is used by NTB for abstract
        # and it may be existing in body_html (from ingested items ?)
        # so we need to remove it here
        p_lead = html_elts.find('p[@class="lead"]')
        if p_lead is not None:
            p_lead.attrib['class'] = "txt-ind"
            try:
                del p_lead.attrib['lede']
            except KeyError:
                pass

        try:
            footer_txt = article['body_footer']
        except KeyError:
            pass
        else:
            body_footer = etree.SubElement(html_elts, 'p', {'class': 'footer-txt'})
            body_footer.text = footer_txt

        # count is done here as superdesk.etree.get_char_count expect a text
        # which would imply a useless serialisation/reparsing
        body_nitf = self.html2nitf(html_elts, attr_remove=["style"])
        body_nitf_text = etree.tostring(body_nitf, encoding='unicode', method='text')
        # we don't want to count line feeds
        char_count = len(body_nitf_text.replace('\n', ''))

        if body_nitf.text:
            # if body_nitf has text, we need to include it in body_content or it will be lost
            # we know that html2nitf always return a <div> without tail, so we don't need to handle tail
            children = body_content.getchildren()
            if children:
                last_child = children[-1]
                last_child.tail = (last_child.tail or '') + body_nitf.text
            else:
                body_content.text = (body_content.text or '') + body_nitf.text
        body_content.extend(body_nitf)
        pubdata = article.pop('pubdata')
        pubdata.set('item-length', str(char_count))
        pubdata.set("unit-of-measure", "character")

        # media
        for data in media_data:
            source = self._get_media_source(data)
            if not source:
                continue

            if data['type'] == CONTENT_TYPE.PICTURE:
                type_ = 'image'
            elif data['type'] == CONTENT_TYPE.GRAPHIC:
                type_ = 'grafikk'
            elif data['type'] == CONTENT_TYPE.VIDEO:
                type_ = 'video'
            else:
                logger.warning("unhandled content type: {}".format(data['type']))
                continue
            mime_type = data.get('mimetype')
            # featured is not None if we have a feature image/media
            # the value of image/media is not used yet but may be in the future
            featured = data.get('_featured')
            if mime_type is None:
                # these default values need to be used if mime_type is not found
                mime_type = 'image/jpeg' if type_ == 'image' or type_ == 'grafikk' else 'video/mpeg'
            caption = self.strip_invalid_chars(data.get('description_text'))
            self._add_media(body_content, type_, mime_type, source, caption, featured)
        media_counter = len(media_data)

        # ntb-media
        try:
            ntb_media = article['extra']['ntb_media']
        except KeyError:
            pass
        else:
            for data in ntb_media:
                mime_type = data['mime_type']
                self._add_media(
                    body_content=body_content,
                    type_=mime_type.split('/')[0],
                    mime_type=mime_type,
                    source=data['url'],
                    caption=data['description_text'],
                    cls='prs',
                    alternate_text='http://www.ntbinfo.no/',
                )
                media_counter += 1

        self._add_meta_media_counter(head, media_counter)

    def _get_media_source(self, data):
        if 'scanpix' in data.get('fetch_endpoint', ''):
            # NTB request that Scanpix ID is used
            # in source for Scanpix media (see SDNTB-229)
            return data['guid']
        else:
            return self._get_original_href(data)

    def _get_original_href(self, data):
        try:
            return data['renditions']['original']['href']
        except KeyError:
            try:
                return next(iter(data['renditions'].values()))['href']
            except (StopIteration, KeyError):
                logger.warning("Can't find source for media {}".format(data.get('guid', '')))

    def _format_body_end(self, article, body_end):
        try:
            emails = [s.strip() for s in article['sign_off'].split('/')]
        except KeyError:
            return
        if emails:
            tagline = etree.SubElement(body_end, 'tagline')
            previous = None
            for email in emails:
                if not email:
                    continue
                a = etree.SubElement(tagline, 'a', {'href': 'mailto:{}'.format(email)})
                a.text = email
                if previous is not None:
                    previous.tail = '/'
                previous = a


PublishService.register_file_extension(NTBNITFFormatter.FORMAT_TYPE, 'xml')
