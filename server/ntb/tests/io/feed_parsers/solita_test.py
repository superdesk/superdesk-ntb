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
        self.assertEqual(item['headline'], 'Signerte veikontrakt på 4 mrd. i Trøndelag')
        self.assertEqual(item['slugline'], 'PRM-NTB-17854111')
        self.assertEqual(item['anpa_category'], [{"name": "Formidlingstjenester", "qcode": "r"}])
        self.assertEqual(item['genre'], [{"name": "Fulltekstmeldinger", "qcode": "Fulltekstmeldinger",
                                          "scheme": "genre_custom"}])

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
            '<p>– Dette er en merkedag for Nye Veier. Nå signerer vi kontrakten for en av våre høyest prioriterte strek'
            'ninger, og det første virkelig store prosjektet i Trøndelag. Med dette er vi i gang i alle våre utbyggings'
            'områder, sier Nye Veiers administrerende direktør, Ingrid Dahl Hovland.</p>\n        <p>ACCIONA Constructi'
            'on er tildelt kontrakten sammen med sine norske underleverandører Multiconsult og Leonhard Nilsen & Sønner'
            '. Entreprisen omfatter prosjektering og bygging av 23 kilometer firefelts motorvei langs dagens E6-trasé. '
            'Det skal også bygges tre tunneler parallelt med de eksisterende, samt en ny tunnel forbi Hommelvik. I pros'
            'jektet inngår totalt åtte bruer og tre toplanskryss.</p>\n        <p>– I et selskap som vårt, der vi legge'
            'r stor vekt på å<em> fornye</em> og <em>forbedre,</em> bør vi også være åpne for at det kan være mye å lær'
            'e av et konsern som bygger infrastruktur i over 40 land, og årlig setter av mer enn to milliarder kroner t'
            'il forskning og utvikling, sier Dahl Hovland.</p>\n        <p>Ny E6 Ranheim–Værnes får i hovedsak en farts'
            'grense på 110 km/t, og utbyggingen vil redusere køer og stimulere til vekst og utvikling i det sammenslått'
            'e Trøndelag. Med fire felt og doble tunnelløp styrkes også trafikksikkerheten betydelig.</p>\n        <p>K'
            'ontrakten mellom ACCIONA Construction og Nye Veier er utformet som en såkalt integrert samhandlingskontrak'
            't, den andre slik type kontrakt Nye Veier inngår på en uke.</p>\n        <p>-Slike kontrakter er til nå sj'
            'eldne i norsk anleggsbransje, og betyr i korthet tett samarbeid med optimalisering og utarbeidelse av regu'
            'leringsplaner i første fase mellom byggherre, entreprenør og rådgiver. Deretter lukkes kontrakten som tota'
            'lentreprise i gjennomføringsfasen, forklarer prosjektdirektør i Nye Veier Trøndelag, Johan Arnt Vatnan.</p'
            '>\n        <p>Byggestart er planlagt i midten av 2019. Prosjektet fullføres i 2024/2025.</p>\n<p class="nt'
            'b-media">\n<a href="https://www.ntbinfo.no/data/images/00775/c7bdf102-9122-4fce-b762-e34353d7a68b.jpg">htt'
            'ps://www.ntbinfo.no/data/images/00775/c7bdf102-9122-4fce-b762-e34353d7a68b.jpg</a><br><a href="https://www'
            '.ntbinfo.no/data/images/00507/26539909-564d-40dc-8298-d237b964dde9.jpg">Kontrakten ble signert i Trondheim'
            ' i dag. Fra venstre: Pablo Garcia Caramés, finanssjef, ACCIONA Construction; Joan Gil, divisjonssjef, ACCI'
            'ONA Construction; Ingrid Dahl Hovland, adm. dir. Nye Veier og Johan Arnt Vatnan, prosjektdir. Nye Veier.</'
            'a>\n</p>\n<h2>Kontakter</h2>\n<p>Ingrid Dahl Hovland \n        Adm. direktør, Nye Veier \n        ingrid.h'
            'ovland@nyeveier.no \n        905 823 34 \n        \n        Johan Arnt Vatnan\n        Prosjektdirektør, N'
            'ye Veier\n        johan.arnt.vatnan@nyeveier.no\n        922 51 113</p>\n<p>Se saken i sin helhet:<br><a h'
            'ref="https://www.ntbinfo.no/pressemelding/signerte-veikontrakt-pa-4-mrd-i-trondelag?releaseId=17854111">ht'
            'tps://www.ntbinfo.no/pressemelding/signerte-veikontrakt-pa-4-mrd-i-trondelag?releaseId=17854111</a></p>'
        )
        self.assertEqual(item['urgency'], 6)
        self.assertEqual(item['ednote'], '*** Dette er en pressemelding formidlet av NTB pva. andre ***')
        self.assertEqual(item['extra']['ntb_pub_name'], 'Nye Veier')

    def test_ntb_media(self):
        item = self.item[0]
        expected = [
            {'description_text': 'https://www.ntbinfo.no/data/images/00775/c7bdf102-9122-4fce-b762-e34353d7a68b.jpg',
             'id': '17854250',
             'mime_type': 'image/jpeg',
             'url': 'https://www.ntbinfo.no/data/images/00775/c7bdf102-9122-4fce-b762-e34353d7a68b.jpg'},
            {'description_text': 'Kontrakten ble signert i Trondheim i dag. Fra venstre: '
                                 'Pablo Garcia Caramés, finanssjef, ACCIONA Construction; '
                                 'Joan Gil, divisjonssjef, ACCIONA Construction; Ingrid '
                                 'Dahl Hovland, adm. dir. Nye Veier og Johan Arnt Vatnan, '
                                 'prosjektdir. Nye Veier.',
             'id': '17854273',
             'mime_type': 'image/jpeg',
             'url': 'https://www.ntbinfo.no/data/images/00507/26539909-564d-40dc-8298-d237b964dde9.jpg'}]

        self.assertEqual(item['extra']['ntb_media'], expected)


class STTBodyTestCase(BaseSolitaTestCase):
    filename = 'solita_2.xml'

    def test_body(self):
        """Check that contacts and images are correctly put in body"""
        item = self.item[0]
        self.assertEqual(
            item['body_html'],
            '<p>– Det offentlige bruker en rekke private leverandører for å levere velferdstjenester over hele landet. '
            'Utvalget skal se på muligheter og problemstillinger knyttet til dette. Det er ikke et utvalg som skal disk'
            'utere for eller mot bruk av private som sådan, men skal kartlegge omfanget av konkurranseutsetting og fore'
            'slå hvordan offentlige\xa0penger kan brukes på best mulig måte, sier næringsminister Torbjørn Røe Isaksen.'
            '</p>\n        <p>Private aktører er viktige bidragsytere i mange velferdstjenester, som for eksempel barne'
            'vern, barnehager og primærhelsetjenesten. Både staten og et stort flertall av kommunene er i dag helt avhe'
            'ngige av private aktører for å levere gode velferdstjenester.</p>\n        <p>– Private aktører kan være e'
            't godt supplement til offentlig tjenesteproduksjon. Samtidig må det offentlige være trygge på at tilbudet '
            'holder god kvalitet, at rettssikkerheten til brukerne ivaretas, og til at det offentlige ikke overbetaler '
            'for slike tjenester. Det er bakgrunnen for vi setter ned dette utvalget, i tråd med det et enstemmig Stort'
            'ing har bedt oss om, sier Røe Isaksen.</p>\n        <p>Ekspertutvalget skal se på i hvilken grad penger so'
            'm bevilges til velferdsformål brukes i tråd med intensjonen. I den grad det ikke er tilfellet skal utvalge'
            't foreslå tiltak som kan bedre situasjonen. Utvalget skal også se på hva som ligger i begrepet "velferdstj'
            'eneste", som det foreløpig ikke finnes en entydig definisjon på. De kan også ta opp tilstøtende problemsti'
            'llinger.</p>\n        <p>Utvalget starter arbeidet høsten 2018, og skal levere sin første delutredning til'
            ' departementet i løpet av et år. I denne delen vil også spørsmål om sikring av arbeidstageres lønns-, pens'
            'jons- og arbeidsvilkår tas opp. Delutredning II skal leveres innen to år.</p>\n        <p>Utvalget skal se'
            ' på flere og ulike sider ved offentlig finansiert tjenesteproduksjon, og har kompetanse innen mikro- og ma'
            'kroøkonomi, finans, skatt, forretningsjus, og spesialkompetanse på velferdstjenester.</p>\n        <p>Dett'
            'e er medlemmene:</p>\n        <p>1. professor Kåre Hagen - leder - Oslo</p>\n        <p>2. seniorrådgiver '
            'Julia Tropina Bakke - medlem - Skedsmo</p>\n        <p>3. stipendiat Gøril Bjerkan - medlem - Bærum</p>\n '
            '       <p>4. professor Trond Bjørnenak- medlem - Bergen</p>\n        <p>5. professor Kari Nyland - medlem '
            '- Trondheim</p>\n        <p>6. kommunaldirektør Camilla Trud Nereid - medlem - Trondheim</p>\n        <p>7'
            '. daglig leder Rolf Røtnes - medlem - Oppegård</p>\n        <p>8. professor Stein Kuhnle - medlem - Bergen'
            '</p>\n        <p>9. advokat Hugo Matre - medlem - Bergen</p>\n        <p>10. avdelingsdirektør Kjerstin Ri'
            'ngdal - medlem – Oppegård</p>\n        <p>Parallelt med denne utredningen foretar Barne- og likestillingsd'
            'epartementet en full gjennomgang av de private barnevernsaktørene. Hensikten er å sørge for riktig bruk av'
            ' private aktører, effektiv ressursbruk og at barna og familienes rettssikkerhet blir godt nok ivaretatt.</'
            'p>\n        <p>Regjeringen har også tatt initiativ til en helhetlig gjennomgang av regelverket og lønnsomh'
            'eten i de private barnehagekjedene. Formålet vil være å legge til rette for en barnehagesektor med langsik'
            'tige og seriøse eiere, som driver barnehager av høy kvalitet og som er opptatt av innovasjon og kostnadsef'
            'fektiv drift.</p>\n        <p>Utvalget som nå nedsette vil være et viktig supplement til disse arbeidene.<'
            '/p>\n<h2>Kontakter</h2>\n<p><name>Pressevakt NFD</name><br><title>Pressevakta er betent mellom 8.00 - 15.4'
            '5 på kvardagar (8.00-15.00 om sumaren).</title><br><phone>902 51 303 (ikkje SMS)</phone><br><email>media@n'
            'fd.dep.no</email></p>\n<p><name>Foo Bar</name><br><title>title</title><br><phone>123 123 123 (ikkje SMS)</'
            'phone><br><email>test@example.net</email></p>\n<p>Se saken i sin helhet:<br><a href="https://www.ntbinfo.n'
            'o/pressemelding/ekspertutvalg-skal-se-pa-bruk-av-private-velferdsleverandorer?releaseId=17854144">https://'
            'www.ntbinfo.no/pressemelding/ekspertutvalg-skal-se-pa-bruk-av-private-velferdsleverandorer?releaseId=17854'
            '144</a></p>'
        )


class STTDocumentsTestCase(BaseSolitaTestCase):
    filename = 'solita_3.xml'

    def test_body(self):
        """Check that documents are correctly put in body"""
        item = self.item[0]
        self.assertEqual(
            item['body_html'],
            '<p>6244 bedrifter har gått overende de siste 12 månedene. Det er en økning på hele 6,6 prosent sammenligne'
            't med samme periode i fjor. \xad– Det er spesielt noen bransjer som merker presset. Butikkene har for leng'
            'st merket kampen mot netthandelen og sliter med lave marginer, forteller Per Einar Ruud i data- og analyse'
            'selskapet Bisnode.</p>\n        <p><strong>Ringvirkninger</strong></p>\n        <p>Mange store kjeder gikk'
            ' overende i 2018, og denne utviklingen har fortsatt inn i 2019. I februar gikk også Hansen & Dysvik konkur'
            's. – Hvis butikkene ikke bestiller varer eller ikke betaler sine leverandører, vil dette gi ringvirkninger'
            ', sier Ruud. Bransjen Lagring og Transport opplever en økning på hele 42,6 prosent i antall konkurser og t'
            'vangsavviklinger hittil i år.</p>\n        <p>To av bransjene som kan ha hatt en positiv påvirkning på feb'
            'ruar-tallene er Bygg og Anlegg samt Tjenesteyting. Bygg og Anlegg har hatt en nedgang på 13,5 prosent hitt'
            'il i år, men står fortsatt for 25,9 prosent av alle konkurser. Tjenesteyting har hatt en nedgang på hele 3'
            '0,9 prosent i samme periode.</p>\n        <p><strong>Størst økning i Hedmark og Nordland</strong></p>\n   '
            '     <p>Hedmark har hatt en økning på 34,5 prosent og Nordland en økning på hele 59 prosent i konkursene h'
            'ittil i år. Mens det stort sett har vært en nedgang i de store næringslivsfylkene som Oslo og Hordaland. A'
            'v de store er det kun Akershus som har en liten oppgang i konkurser i 2019.</p>\n        <p>– Det er mange'
            ' faktorer som bestemmer om bedriften overlever i markedet. Blant annet innkjøp, bransjeutvikling, rammebet'
            'ingelser, markedsføring og kundeopplevelser. Men det er i hvert fall en ting man kan gjøre noe med for å u'
            'nngå konkurs, og det er å følge godt med på de man handler med og være tilbakeholden med kreditter til vir'
            'ksomheter som sliter, råder Ruud.</p>\n<p class="ntb-media">\n<a href="https://www.ntbinfo.no/data/images/'
            '00390/20b6d51e-3abb-4eff-ae86-c4dfff029a23.jpg">6244 bedrifter har gått overende de siste 12 månedene. Spe'
            'sielt Detaljhandel, Lagring og Transport merker presset. (foto for fri bruk til saken)</a><br><a href="htt'
            'ps://www.ntbinfo.no/data/images/00749/e303f05c-30ad-4821-8862-d0f1f27d484a.jpg">– Det er spesielt noen bra'
            'nsjer som merker presset. Butikkene har for lengst merket kampen mot netthandelen og sliter med lave margi'
            'ner, forteller Per Einar Ruud i data- og analyseselskapet Bisnode.</a>\n</p>\n<h2>Kontakter</h2>\n<p><name'
            '>Per Einar Ruud i Bisnode</name><br><title>Kredittøkonom, Bisnode</title><br><phone>+47 92 40 10 04\u2028<'
            '/phone><br><email>per.einar.ruud@bisnode.com</email></p>\n<h2>Dokumenter</h2><p>\n<a href="https://www.ntb'
            'info.no/data/attachments/00203/fa42f1c1-aaa5-4ec1-908d-8b38a100bfab.pptx">Konkurser februar 2019.pptx</a>'
            '\n</p>\n<p>Se saken i sin helhet:<br><a href="https://www.ntbinfo.no/pressemelding/nedgang-men-fortsatt-ho'
            'ye-konkurstall-med-bransje--og-fylkesoversikt?releaseId=17861325">https://www.ntbinfo.no/pressemelding/ned'
            'gang-men-fortsatt-hoye-konkurstall-med-bransje--og-fylkesoversikt?releaseId=17861325</a></p>'
        )


class STTDocumentWithContactsAsTextCase(BaseSolitaTestCase):
    """This test use a file which contains a <contactsAsText> element"""
    filename = 'solita_4.xml'

    def test_body(self):
        """Check that body is as expected (SDNTB-591 regression test)"""
        item = self.item[0]
        self.assertEqual(
            item['body_html'],
            '<p>DETTE ER EN TEST BRØDTEKST</p>\n<p class="ntb-media">\n<a href="https://www.ntbinfo.no/data/images/0063'
            '3/c0973bb9-ae50-4dd6-8e83-3bdabd4dea5d.jpg">Dette er en test bildetekst</a>\n</p>\n<h2>Kontakter</h2>\n<p>'
            'Dette er en test kontaktperson</p>\n<p>Se saken i sin helhet:<br><a href="https://www.ntbinfo.no/pressemel'
            'ding/dette-er-en-test-tittel?releaseId=17867709">https://www.ntbinfo.no/pressemelding/dette-er-en-test-tit'
            'tel?releaseId=17867709</a></p>'
        )
