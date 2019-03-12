# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from ntb.io.feed_parsers.solita import SolitaFeedParser
from . import XMLParserTestCase


class BaseSolitaTestCase(XMLParserTestCase):
    def setUp(self):
        self.parser = SolitaFeedParser()
        super().setUp()


class STTTestCase(BaseSolitaTestCase):
    filename = 'solita_1.xml'

    def test_can_parse(self):
        """Check that can_parse return True on solita file"""
        self.assertTrue(SolitaFeedParser().can_parse(self.xml_root))

    def test_content(self):
        """Check majors metadata"""
        item = self.item[0]
        self.assertEqual(item['guid'], 'solita-123123-17854111')
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['firstpublished'].isoformat(), '2018-09-28T11:15:00')
        self.assertEqual(item['headline'], 'PRM: Nye Veier / Signerte veikontrakt på 4 mrd. i Trøndelag')
        self.assertEqual(item['slugline'], 'PRM-NTB-17854111')
        self.assertEqual(item['anpa_category'], [{"name": "Formidlingstjenester", "qcode": "r"}])
        self.assertEqual(item['genre'], [{"name": "Fulltekstmeldinger", "qcode": "Fulltekstmeldinger"}])

        self.assertIn(
            {'qcode': 'PRM-NTB',
             'name': 'PRM-NTB',
             'scheme': 'category'},
            item['subject'])
        self.assertEqual(item['original_source'], '14424980')
        self.assertEqual(
            item['abstract'],
            'Nye Veier har signert kontrakt med det spanske konsernet ACCIONA '
            'Construction om E6-utbygging i Trøndelag, mellom Ranheim og '
            'Værnes. Kontrakten er en totalentreprise verdt ca. 4 milliarder '
            'kroner, det vil si en av landets største veikontrakter.')

        self.assertEqual(
            item['body_html'],
            '<p>&ndash; Dette er en merkedag for Nye Veier. N&aring; signerer vi kontrakten for en av v&aring;re h&osla'
            'sh;yest prioriterte strekninger, og det f&oslash;rste virkelig store prosjektet i Tr&oslash;ndelag. Med de'
            'tte er vi i gang i alle v&aring;re utbyggingsomr&aring;der, sier Nye Veiers administrerende direkt&oslash;'
            'r, Ingrid Dahl Hovland.</p>\n        <p>ACCIONA Construction er tildelt kontrakten sammen med sine norske '
            'underleverand&oslash;rer Multiconsult og Leonhard Nilsen &amp; S&oslash;nner. Entreprisen omfatter prosjek'
            'tering og bygging av 23 kilometer firefelts motorvei langs dagens E6-tras&eacute;. Det skal ogs&aring; byg'
            'ges tre tunneler parallelt med de eksisterende, samt en ny tunnel forbi Hommelvik. I prosjektet inng&aring'
            ';r totalt &aring;tte bruer og tre toplanskryss.</p>\n        <p>&ndash; I et selskap som v&aring;rt, der v'
            'i legger stor vekt p&aring; &aring;<em> fornye</em> og <em>forbedre,</em> b&oslash;r vi ogs&aring; v&aelig'
            ';re &aring;pne for at det kan v&aelig;re mye &aring; l&aelig;re av et konsern som bygger infrastruktur i o'
            'ver 40 land, og &aring;rlig setter av mer enn to milliarder kroner til forskning og utvikling, sier Dahl H'
            'ovland.</p>\n        <p>Ny E6 Ranheim&ndash;V&aelig;rnes f&aring;r i hovedsak en fartsgrense p&aring; 110 '
            'km/t, og utbyggingen vil redusere k&oslash;er og stimulere til vekst og utvikling i det sammensl&aring;tte'
            ' Tr&oslash;ndelag. Med fire felt og doble tunnell&oslash;p styrkes ogs&aring; trafikksikkerheten betydelig'
            '.</p>\n        <p>Kontrakten mellom ACCIONA Construction og Nye Veier er utformet som en s&aring;kalt inte'
            'grert samhandlingskontrakt, den andre slik type kontrakt Nye Veier inng&aring;r p&aring; en uke.</p>\n    '
            '    <p>-Slike kontrakter er til n&aring; sjeldne i norsk anleggsbransje, og betyr i korthet tett samarbeid'
            ' med optimalisering og utarbeidelse av reguleringsplaner i f&oslash;rste fase mellom byggherre, entrepren&'
            'oslash;r og r&aring;dgiver. Deretter lukkes kontrakten som totalentreprise i gjennomf&oslash;ringsfasen, f'
            'orklarer prosjektdirekt&oslash;r i Nye Veier Tr&oslash;ndelag, Johan Arnt Vatnan.</p>\n        <p>Byggesta'
            'rt er planlagt i midten av 2019. Prosjektet fullf&oslash;res i 2024/2025.</p>\n<p>\n<a href="https://www.n'
            'tbinfo.no/data/images/00775/c7bdf102-9122-4fce-b762-e34353d7a68b.jpg">https://www.ntbinfo.no/data/images/0'
            '0775/c7bdf102-9122-4fce-b762-e34353d7a68b.jpg</a><br><a href="https://www.ntbinfo.no/data/images/00507/265'
            '39909-564d-40dc-8298-d237b964dde9.jpg">Kontrakten ble signert i Trondheim i dag. Fra venstre: Pablo Garcia'
            ' Caramés, finanssjef, ACCIONA Construction; Joan Gil, divisjonssjef, ACCIONA Construction; Ingrid Dahl Hov'
            'land, adm. dir. Nye Veier og Johan Arnt Vatnan, prosjektdir. Nye Veier.</a>\n</p>\n<p>Les hele denne saken'
            ' fra <name>Nye Veier</name> på NTB info<br><a href="https://www.ntbinfo.no/pressemelding/signerte-veikontr'
            'akt-pa-4-mrd-i-trondelag?releaseId=17854111">https://www.ntbinfo.no/pressemelding/signerte-veikontrakt-pa-'
            '4-mrd-i-trondelag?releaseId=17854111</a></p>')
        self.assertEqual(item['urgency'], 6)
        self.assertEqual(item['ednote'], '**** NTBs PRESSEMELDINGSTJENESTE - Se www.ntbinfo.no ****')


class STTBodyTestCase(BaseSolitaTestCase):
    filename = 'solita_2.xml'

    def test_body(self):
        """Check that contacts and images are correctly put in body"""
        item = self.item[0]
        self.assertEqual(
            item['body_html'],
            '<p>&ndash; Det offentlige bruker en rekke private leverand&oslash;rer for &aring; levere velferdstjenester'
            ' over hele landet. Utvalget skal se p&aring; muligheter og problemstillinger knyttet til dette. Det er ikk'
            'e et utvalg som skal diskutere for eller mot bruk av private som s&aring;dan, men skal kartlegge omfanget '
            'av konkurranseutsetting og foresl&aring; hvordan offentlige&nbsp;penger kan brukes p&aring; best mulig m&a'
            'ring;te, sier n&aelig;ringsminister Torbj&oslash;rn R&oslash;e Isaksen.</p>\n        <p>Private akt&oslash'
            ';rer er viktige bidragsytere i mange velferdstjenester, som for eksempel barnevern, barnehager og prim&ael'
            'ig;rhelsetjenesten. B&aring;de staten og et stort flertall av kommunene er i dag helt avhengige av private'
            ' akt&oslash;rer for &aring; levere gode velferdstjenester.</p>\n        <p>&ndash; Private akt&oslash;rer '
            'kan v&aelig;re et godt supplement til offentlig tjenesteproduksjon. Samtidig m&aring; det offentlige v&ael'
            'ig;re trygge p&aring; at tilbudet holder god kvalitet, at rettssikkerheten til brukerne ivaretas, og til a'
            't det offentlige ikke overbetaler for slike tjenester. Det er bakgrunnen for vi setter ned dette utvalget,'
            ' i tr&aring;d med det et enstemmig Storting har bedt oss om, sier R&oslash;e Isaksen.</p>\n        <p>Eksp'
            'ertutvalget skal se p&aring; i hvilken grad penger som bevilges til velferdsform&aring;l brukes i tr&aring'
            ';d med intensjonen. I den grad det ikke er tilfellet skal utvalget foresl&aring; tiltak som kan bedre situ'
            'asjonen. Utvalget skal ogs&aring; se p&aring; hva som ligger i begrepet "velferdstjeneste", som det forel&'
            'oslash;pig ikke finnes en entydig definisjon p&aring;. De kan ogs&aring; ta opp tilst&oslash;tende problem'
            'stillinger.</p>\n        <p>Utvalget starter arbeidet h&oslash;sten 2018, og skal levere sin f&oslash;rste'
            ' delutredning til departementet i l&oslash;pet av et &aring;r. I denne delen vil ogs&aring; sp&oslash;rsm&'
            'aring;l om sikring av arbeidstageres l&oslash;nns-, pensjons- og arbeidsvilk&aring;r tas opp. Delutredning'
            ' II skal leveres innen to &aring;r.</p>\n        <p>Utvalget skal se p&aring; flere og ulike sider ved off'
            'entlig finansiert tjenesteproduksjon, og har kompetanse innen mikro- og makro&oslash;konomi, finans, skatt'
            ', forretningsjus, og spesialkompetanse p&aring; velferdstjenester.</p>\n        <p>Dette er medlemmene:</p'
            '>\n        <p>1. professor K&aring;re Hagen - leder - Oslo</p>\n        <p>2. seniorr&aring;dgiver Julia T'
            'ropina Bakke - medlem - Skedsmo</p>\n        <p>3. stipendiat G&oslash;ril Bjerkan - medlem - B&aelig;rum<'
            '/p>\n        <p>4. professor Trond Bj&oslash;rnenak- medlem - Bergen</p>\n        <p>5. professor Kari Nyl'
            'and - medlem - Trondheim</p>\n        <p>6. kommunaldirekt&oslash;r Camilla Trud Nereid - medlem - Trondhe'
            'im</p>\n        <p>7. daglig leder Rolf R&oslash;tnes - medlem - Oppeg&aring;rd</p>\n        <p>8. profess'
            'or Stein Kuhnle - medlem - Bergen</p>\n        <p>9. advokat Hugo Matre - medlem - Bergen</p>\n        <p>'
            '10. avdelingsdirekt&oslash;r Kjerstin Ringdal - medlem &ndash; Oppeg&aring;rd</p>\n        <p>Parallelt me'
            'd denne utredningen foretar Barne- og likestillingsdepartementet en full gjennomgang av de private barneve'
            'rnsakt&oslash;rene. Hensikten er &aring; s&oslash;rge for riktig bruk av private akt&oslash;rer, effektiv '
            'ressursbruk og at barna og familienes rettssikkerhet blir godt nok ivaretatt.</p>\n        <p>Regjeringen '
            'har ogs&aring; tatt initiativ til en helhetlig gjennomgang av regelverket og l&oslash;nnsomheten i de priv'
            'ate barnehagekjedene. Form&aring;let vil v&aelig;re &aring; legge til rette for en barnehagesektor med lan'
            'gsiktige og seri&oslash;se eiere, som driver barnehager av h&oslash;y kvalitet og som er opptatt av innova'
            'sjon og kostnadseffektiv drift.</p>\n        <p>Utvalget som n&aring; nedsette vil v&aelig;re et viktig su'
            'pplement til disse arbeidene.</p>\n<h2>Kontacter</h2><p><name>Pressevakt NFD</name><br><title>Pressevakta '
            'er betent mellom 8.00 - 15.45 på kvardagar (8.00-15.00 om sumaren).</title><br><phone>902 51 303 (ikkje SM'
            'S)</phone><br><email>media@nfd.dep.no</email></p>\n<p>Les hele denne saken fra <name>Nærings- og fiskeride'
            'partementet</name> på NTB info<br><a href="https://www.ntbinfo.no/pressemelding/ekspertutvalg-skal-se-pa-b'
            'ruk-av-private-velferdsleverandorer?releaseId=17854144">https://www.ntbinfo.no/pressemelding/ekspertutvalg'
            '-skal-se-pa-bruk-av-private-velferdsleverandorer?releaseId=17854144</a></p>')


class STTDocumentsTestCase(BaseSolitaTestCase):
    filename = 'solita_3.xml'

    def test_body(self):
        """Check that documents are correctly put in body"""
        item = self.item[0]
        self.assertEqual(
            item['body_html'],
            '<p>6244 bedrifter har g&aring;tt overende de siste 12 m&aring;nedene. Det er en &oslash;kning p&aring; hel'
            'e 6,6 prosent sammenlignet med samme periode i fjor. &shy;&ndash; Det er spesielt noen bransjer som merker'
            ' presset. Butikkene har for lengst merket kampen mot netthandelen og sliter med lave marginer, forteller P'
            'er Einar Ruud i data- og analyseselskapet Bisnode.</p>\n        <p><strong>Ringvirkninger</strong></p>\n  '
            '      <p>Mange store kjeder gikk overende i 2018, og denne utviklingen har fortsatt inn i 2019. I februar '
            'gikk ogs&aring; Hansen &amp; Dysvik konkurs. &ndash; Hvis butikkene ikke bestiller varer eller ikke betale'
            'r sine leverand&oslash;rer, vil dette gi ringvirkninger, sier Ruud. Bransjen Lagring og Transport opplever'
            ' en &oslash;kning p&aring; hele 42,6 prosent i antall konkurser og tvangsavviklinger hittil i &aring;r.</p'
            '>\n        <p>To av bransjene som kan ha hatt en positiv p&aring;virkning p&aring; februar-tallene er Bygg'
            ' og Anlegg samt Tjenesteyting. Bygg og Anlegg har hatt en nedgang p&aring; 13,5 prosent hittil i &aring;r,'
            ' men st&aring;r fortsatt for 25,9 prosent av alle konkurser. Tjenesteyting har hatt en nedgang p&aring; he'
            'le 30,9 prosent i samme periode.</p>\n        <p><strong>St&oslash;rst &oslash;kning i Hedmark og Nordland'
            '</strong></p>\n        <p>Hedmark har hatt en &oslash;kning p&aring; 34,5 prosent og Nordland en &oslash;k'
            'ning p&aring; hele 59 prosent i konkursene hittil i &aring;r. Mens det stort sett har v&aelig;rt en nedgan'
            'g i de store n&aelig;ringslivsfylkene som Oslo og Hordaland. Av de store er det kun Akershus som har en li'
            'ten oppgang i konkurser i 2019.</p>\n        <p>&ndash; Det er mange faktorer som bestemmer om bedriften o'
            'verlever i markedet. Blant annet innkj&oslash;p, bransjeutvikling, rammebetingelser, markedsf&oslash;ring '
            'og kundeopplevelser. Men det er i hvert fall en ting man kan gj&oslash;re noe med for &aring; unng&aring; '
            'konkurs, og det er &aring; f&oslash;lge godt med p&aring; de man handler med og v&aelig;re tilbakeholden m'
            'ed kreditter til virksomheter som sliter, r&aring;der Ruud.</p>\n<p>\n<a href="https://www.ntbinfo.no/data'
            '/images/00390/20b6d51e-3abb-4eff-ae86-c4dfff029a23.jpg">6244 bedrifter har gått overende de siste 12 måned'
            'ene. Spesielt Detaljhandel, Lagring og Transport merker presset. (foto for fri bruk til saken)</a><br><a h'
            'ref="https://www.ntbinfo.no/data/images/00749/e303f05c-30ad-4821-8862-d0f1f27d484a.jpg">– Det er spesielt '
            'noen bransjer som merker presset. Butikkene har for lengst merket kampen mot netthandelen og sliter med la'
            've marginer, forteller Per Einar Ruud i data- og analyseselskapet Bisnode.</a>\n</p>\n<h2>Dokumenter</h2><'
            'p>\n<a href="https://www.ntbinfo.no/data/attachments/00203/fa42f1c1-aaa5-4ec1-908d-8b38a100bfab.pptx">Konk'
            'urser februar 2019.pptx</a>\n</p>\n<h2>Kontacter</h2><p><name>Per Einar Ruud i Bisnode</name><br><title>Kr'
            'edittøkonom, Bisnode</title><br><phone>+47 92 40 10 04\u2028</phone><br><email>per.einar.ruud@bisnode.com<'
            '/email></p>\n<p>Les hele denne saken fra <name>Bisnode</name> på NTB info<br><a href="https://www.ntbinfo.'
            'no/pressemelding/nedgang-men-fortsatt-hoye-konkurstall-med-bransje--og-fylkesoversikt?releaseId=17861325">'
            'https://www.ntbinfo.no/pressemelding/nedgang-men-fortsatt-hoye-konkurstall-med-bransje--og-fylkesoversikt?'
            'releaseId=17861325</a></p>')
