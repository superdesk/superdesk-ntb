# -*- coding: utf-8 -*
"""
    Getting currency exchange rates for today and yesterday. The source is an XML file
    Source of data is http://www.ecb.int/stats/eurofxref/eurofxref-hist-90d.xml

    (c) NTB 2007-: Trond Husoe (510 / thu@ntb.no)
    This solution gets data form http://www.dnbnor.no until the bank of norway sets up an xml-feed.
    Version 0.9
    Corrected fetching data from ebc and corrected decimals
"""

import xml.etree.cElementTree as ElementTree
import urllib3
import datetime

currencies = [
    {'currency': 'USD', 'name': 'US dollar', 'multiplication': 1},
    {'currency': 'NOK', 'name': 'Euro', 'multiplication': 0},
    {'currency': 'CHF', 'name': 'Sveitsiske franc', 'multiplication': 100},
    {'currency': 'DKK', 'name': 'Danske kroner', 'multiplication': 100},
    {'currency': 'GBP', 'name': 'Britiske pund', 'multiplication': 1},
    {'currency': 'SEK', 'name': 'Svenske kroner', 'multiplication': 100},
    {'currency': 'CAD', 'name': 'Canadiske dollar', 'multiplication': 1},
    {'currency': 'JPY', 'name': 'Japanske yen', 'multiplication': 100}
]

template = '<tr><td>{name}&nbsp;({currency})</td><td>{today}</td><td>({yesterday})</td></tr>'


def generate_row(currency, currency_name, multiplication, euro_currency, yesterday_euro,
                 today_currency, yesterday_currency):
    today_rate = today_currency if multiplication == 0 else ''
    yesterday_rate = yesterday_currency if multiplication == 0 else ''

    if today_currency and multiplication:
        today_rate = "{0:.4f}".format(float(euro_currency) * multiplication / float(today_currency))

    if yesterday_currency and multiplication:
        yesterday_rate = "{0:.4f}".format(float(yesterday_euro) * multiplication / float(yesterday_currency))

    if currency == "NOK":
        currency = "EUR"

    yesterday_rate = yesterday_rate.replace('.', ',')
    today_rate = today_rate.replace('.', ',')
    return template.format(currency=currency, name=currency_name, today=today_rate, yesterday=yesterday_rate)


def get_currency(today_date):
    try:

        number_of_days_to_yesterday = 1

        # removed the today() call on today_date date. Otherwise we are just setting a new date (today)
        if today_date.weekday() == 0:
            number_of_days_to_yesterday = 3

        yesterday_date = today_date - datetime.timedelta(number_of_days_to_yesterday)

        # Getting data from The European Central Bank
        url_xml = "http://www.ecb.int/stats/eurofxref/eurofxref-hist-90d.xml"
        http = urllib3.PoolManager()
        response = http.request('GET', url_xml, headers={'User-Agent': 'Mozilla/5.0'})
        xml_doc = response.data.decode('UTF-8')

        # Setting up the xml document
        doc = ElementTree.fromstring(xml_doc)
        namespaces = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
                      'eurofxref': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}

        xpath_euro_string = ".//eurofxref:Cube[@time='{date}']/eurofxref:Cube[@currency='NOK']"

        euro_query = doc.find(xpath_euro_string.format(date=today_date.date()), namespaces)
        if euro_query is None:
            return ['Dagens valutakurser ikke klare ennå']

        euro = euro_query.attrib["rate"]

        yesterday_euro_query = doc.find(xpath_euro_string.format(date=yesterday_date.date()), namespaces)

        yesterday_euro = yesterday_euro_query.attrib["rate"]

        # This is the currencies for today
        all_currencies = ".//eurofxref:Cube[@time='{date}']/eurofxref:Cube"

        nodes_today = doc.findall(all_currencies.format(date=today_date.date()), namespaces)

        today_dictionary = {cube.attrib["currency"]: cube.attrib["rate"] for cube in nodes_today}

        nodes_yesterday = doc.findall(all_currencies.format(date=yesterday_date.date()), namespaces)

        yesterday_dictionary = {cube.attrib["currency"]: cube.attrib["rate"] for cube in nodes_yesterday}

        array_store_string = [generate_row(currency['currency'], currency['name'], currency['multiplication'], euro,
                                           yesterday_euro,
                                           today_dictionary.get(currency['currency'], ''),
                                           yesterday_dictionary.get(currency['currency'], ''))
                              for currency in currencies]

        return array_store_string

    except Exception as ex:
        return ['Error: ', str(ex)]


def ntb_currency_macro(item, **kwargs):
    # headline
    # this one is the correct one, just that the clock is past 00:00 datetime.datetime.now().date()
    # This date is created just because we want to test monday error
    # comment the line below out if you want to test against a specific day
    # today_date = datetime.datetime.today() - datetime.timedelta(3)
    today_date = datetime.datetime.now()

    # Setting days to go backwards to one, unless it is Monday. Then we go three days back (Friday)
    number_of_days_to_yesterday = 1
    if today_date.weekday() == 0:
        # Monday
        number_of_days_to_yesterday = 3
    elif today_date.weekday() == 6:
        # Sunday - just in case someone decides to run this macro on a Sunday
        today_date = datetime.datetime.today() - datetime.timedelta(2)
        number_of_days_to_yesterday = 3
    elif today_date.weekday() == 5:
        # Saturday - just in case someone decides to run this macro on a Saturday
        today_date = datetime.datetime.today() - datetime.timedelta(1)
        number_of_days_to_yesterday = 2

    yesterday_date = today_date - datetime.timedelta(number_of_days_to_yesterday)
    headline = "Valutakurser {} ({})"
    headline = headline.format(today_date.strftime("%d.%m"), yesterday_date.strftime("%d.%m"))
    abstract = "Representative markedskurser for valuta fra Norges Bank"

    item['headline'] = headline
    item['abstract'] = abstract
    item['body_html'] = '<table>' + ''.join(line for line in get_currency(today_date)) + '</table>'

    return item


# Set the name to be NTB Currency Macro
name = 'NTB Currency Macro'

# Set the label to be NTB Currency Macro
label = 'NTB Currency Macro'

# Call the macro function
callback = ntb_currency_macro

# define the access type
access_type = 'frontend'

# Define the action type
action_type = 'direct'
