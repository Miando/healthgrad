import scrapy
from __future__ import absolute_import
from healthgrades.items import InsuranceItem
from nameparser import HumanName
from w3lib.html import remove_tags
import json
import string


class ElevenSpider(scrapy.Spider):
    name = "1199"
    custom_settings ={
        # 'DOWNLOAD_DELAY': 2,
        # 'ROBOTSTXT_OBEY': False,
        # 'COOKIES_ENABLED': False
        # 'USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/52.0'
    }
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
              "NM", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "NJ", "NY"]
    search = []
    n=0

    def start_requests(self):
        a=1
        url = 'http://mxr02.1199funds.org/idirectory/default.asp'
        yield scrapy.Request(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Upgrade-Insecure-Requests': '1',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
                # 'Content-type': 'json'
            },
            callback=self.parse2
        )

    def parse2(self, response):
        first = string.ascii_uppercase
        last = string.ascii_uppercase
        for state in self.states:
            for f in first:
                for l in last:
                    text = (state+' '+f+' '+l)
                    self.search = self.search + [text.split()]
        variant = self.search.pop()
        yield scrapy.FormRequest(
            url='http://mxr02.1199funds.org/idirectory/applicationspecific/search.asp',
            formdata={
                "posted":"posted",
                "Institution":"ProvidersOnly",
                "LastName":variant[2],
                "FirstName":variant[1],
                "c_state":"{}++++++++++++++++++".format(variant[0]),
                "distance":"0",
                "current_page":"2",
            },
            meta={'state': variant[0]},
            callback=self.parse_table
        )

    def parse_table(self, response):
        links = response.xpath('//td[@class="tablevalue"]/a/@href').re('AddressDetails.+')
        len_links = len(links)
        for link in links:
            yield scrapy.Request(
                url='http://mxr02.1199funds.org/idirectory/applicationspecific/{}'.format(link),
                headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Upgrade-Insecure-Requests': '1',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
                    # 'Content-type': 'json'
                },
                meta={'len_links': len_links, 'state': response.meta['state']},
                callback=self.parse_item
            )
        if not links:
            variant = self.search.pop()
            print(variant)
            yield scrapy.FormRequest(
                url='http://mxr02.1199funds.org/idirectory/applicationspecific/search.asp',
                formdata={
                    "posted": "posted",
                    "Institution": "ProvidersOnly",
                    "LastName": variant[2],
                    "FirstName": variant[1],
                    "c_state": "{}++++++++++++++++++".format(variant[0]),
                    "distance": "0",
                    "current_page": "2",
                },
                meta={'state': variant[0]},
                dont_filter=True,
                callback=self.parse_table
            )

    def parse_item(self, response):
        self.n = self.n + 1
        i = InsuranceItem()
        full_name = response.xpath('//a[contains(@href, "providerdetails")]/text()').extract_first()
        i['full_name'] = full_name
        i['url'] = response.url
        if full_name:
            name = HumanName(full_name)
            i['first_name'] = name.first
            i['last_name'] = name.last
        i['speciality'] = response.xpath('//h4[@class="media-subheading"]/a/text()').extract_first(default='')
        i['city'] = response.xpath('//td[@class="tablevalue"]/text()').re_first('(.+?),\s[A-Z][A-Z]')
        i['state'] = response.meta.get('state')
        i['general_plan'] = ''
        i['plans'] = ', '.join(response.xpath('//span[@id="plans_accepted"]//p[@class="text-success"]/text()').re('\S.+'))
        yield i
        if response.meta.get('len_links') == self.n:
            self.n = 0
            variant = self.search.pop()
            yield scrapy.FormRequest(
                url='http://mxr02.1199funds.org/idirectory/applicationspecific/search.asp',
                formdata={
                    "posted": "posted",
                    "Institution": "ProvidersOnly",
                    "LastName": variant[2],
                    "FirstName": variant[1],
                    "c_state": "{}++++++++++++++++++".format(variant[0]),
                    "distance": "0",
                    "current_page": "2",
                },
                meta={'state': variant[0]},
                dont_filter=True,
                callback=self.parse_table
            )
