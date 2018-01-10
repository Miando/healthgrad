import scrapy
from healthgrades.items import InsuranceItem
from nameparser import HumanName
from w3lib.html import remove_tags
import json


class AmerihealthSpider(scrapy.Spider):
    name = "amerihealth"
    # start_urls = ['https://ibxweb.healthsparq.com/healthsparq/public/service/search/point?alphaPrefix=&isPromotionSearch=true&key=&location=United States&maxLatitude=&maxLongitude=&minLatitude=&minLongitude=&page=1&providerType=&query=doctor&radius=25&size=10&searchResultsTab=Local&searchType=default&searchCategory=&sort=DEFAULT&waitForOop=false&doWebAlert=true&productCode=all&usersTimeZoneInMinutes=120&guid=c436e4f7-339e-4cab-9cd3-d86c4f5f24d7&_=1515019166115']
    custom_settings ={
        'ROBOTSTXT_OBEY': False,
        # 'COOKIES_ENABLED': False
        # 'USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/52.0'
    }


    def start_requests(self):
        a=1
        url = 'https://ibxweb.healthsparq.com/healthsparq/public/service/login?city=Cranbury&state=NJ&country=&insurerCode=IBXRED_I&brandCode=IBXREDAHNJCOMM&productCode=all&_=1515082386590'
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
            meta={'cookiejar': a},
            callback=self.parse2
        )

    def parse2(self, response):
        for page in range(1, 7458):
            yield scrapy.Request(
                url='https://ibxweb.healthsparq.com/healthsparq/public/service/search/point?alphaPrefix=&isPromotionSearch=true&key=&location=United%20States&maxLatitude=&maxLongitude=&minLatitude=&minLongitude=&page={}&providerType=&query=&radius=25&size=10&searchResultsTab=Local&searchType=default&searchCategory=&sort=DEFAULT&waitForOop=false&doWebAlert=true&usersTimeZoneInMinutes=120&guid=28c2c154-a61d-4806-abbe-9447e1ab24da'.format(str(page)),#&guid=9bf993c0-5c0d-415e-8d2f-fbfb35c89d45
                headers={
                    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Upgrade-Insecure-Requests': '1',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
                    # 'Content-type': 'json'
                },
                meta={'cookiejar': response.meta.get('cookiejar')},
                callback=self.parse_item
            )
            # break

    def parse_item(self, response):
        data = json.loads(response.body.decode())
        for t in data['providers']:
            i = InsuranceItem()
            full_name = t['fullName']
            i['full_name'] = full_name
            i['url'] = ''
            i['first_name'] = t['firstName']
            if t['firstName']:
                i['last_name'] = t['lastName']
                speciality = []
                for s in t['providerSpecialties']:
                    speciality = speciality + [s['specialtyName']]
                i['speciality'] = ', '.join(speciality)
                i['city'] = t['bestLocation']['city']
                i['state'] = t['bestLocation']['state']
                i['general_plan'] = ''
                all_plans = []
                plans = t['bestLocation']['acceptedPlans']
                for p in plans:
                    for s in p['subPlans']:
                        for u in s['subPlans']:
                            all_plans = all_plans + [u['name']]
                i['plans'] = ', '.join(list(set(all_plans)))
                yield i