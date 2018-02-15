import scrapy
import json
from healthgrades.items import FullItem
from inline_requests import inline_requests
from nameparser import HumanName


class InsuranceHealthgradSpider(scrapy.Spider):
    name = "healthgrad_full"
    start_urls = ['https://www.healthgrades.com/specialty-directory']
    custom_settings ={
        'ROBOTSTXT_OBEY': False
    }
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    def parse(self, response):
        # print(response.body)
        specialisations = response.xpath('//a[@data-hgoname="specialty-link"]/text()').extract()
        for state in self.states:
            for specialisation in specialisations:
                yield scrapy.Request(
                    url='https://www.healthgrades.com/api3/usearch?userLocalTime=1:49&what={}&where={}&isStateOnly=true&sort.provider=bestmatch&category=provider&sessionId=S69f41e8712abf8ff&requestId=R345ead5aab2604d9&pageSize.provider=36&pageNum=1&isFirstRequest=true&debug=false&isAtlas=false'
                        .format(specialisation, state),
                    meta={
                        'state': state,
                        'specialisation': specialisation,
                    },
                    callback=self.categories
                )

    def categories(self, response):
        page = json.loads(response.body.decode())
        count = page['search']['searchResults']['provider']['totalCount']
        if count != '0':
            for li in page['search']['searchResults']['provider']['results']:
                try:
                    age = li['age']
                    images = ['https:' + li['imagePaths'][0]]
                    office_address = li['address']
                    gender = li['gender']
                    full_name = li['displayName']
                    name = HumanName(li['displayName'])
                    first_name = name.first
                    last_name = name.last
                    midle_name = name.middle
                    specialty = li['specialty']
                    subspecialty = li['specialistDesc']
                    yield scrapy.Request(
                        url='https://www.healthgrades.com' + li['providerUrl'],
                        meta={
                            'office_address': office_address,
                            'age': age,
                            'images': images,
                            'subspecialty': subspecialty,
                            'midle_name': midle_name,
                            'full_name': full_name,
                            'first_name': first_name,
                            'gender': gender,
                            'last_name': last_name,
                            'specialty': specialty,
                            'state': response.meta['state'],
                        },
                        callback=self.parse_item
                    )
                except:
                    pass
            pages = int(int(count)/36)
            if pages > 0:
                for n in range(2, pages + 1):
                    yield scrapy.Request(
                        url='https://www.healthgrades.com/api3/usearch?userLocalTime=1:49&what={}&where={}&isStateOnly=true&sort.provider=bestmatch&category=provider&sessionId=S69f41e8712abf8ff&requestId=R345ead5aab2604d9&pageSize.provider=36&pageNum={}&isFirstRequest=true&debug=false&isAtlas=false'
                            .format(response.meta['specialisation'], response.meta['state'], str(n)),
                        meta={
                            'state': response.meta['state'],
                            'specialisation': response.meta['specialisation'],
                        },
                        callback=self.categories2
                    )

    def categories2(self, response):
        page = json.loads(response.body.decode())
        for li in page['search']['searchResults']['provider']['results']:
            try:
                age = li['age']
                images = ['https:' + li['imagePaths'][0]]
                print(images)
                office_address = li['address']
                gender = li['gender']
                full_name = li['displayName']
                name = HumanName(li['displayName'])
                first_name = name.first
                last_name = name.last
                midle_name = name.middle
                specialty = li['specialty']
                subspecialty = li['specialistDesc']
                yield scrapy.Request(
                    url='https://www.healthgrades.com' + li['providerUrl'],
                    meta={
                        'office_address': office_address,
                        'age': age,
                        'images': images,
                        'subspecialty': subspecialty,
                        'midle_name': midle_name,
                        'full_name': full_name,
                        'first_name': first_name,
                        'gender': gender,
                        'last_name': last_name,
                        'specialty': specialty,
                        'state': response.meta['state'],
                    },
                    callback=self.parse_item
                )
            except:
                pass

    @inline_requests
    def parse_item(self, response):
        i = {}
        education = []
        for ed in response.xpath('//section[@data-qa-target="learn-education-section"]//ul/li'):
            education_info = {}
            name = ed.xpath('./div[1]/text()').extract_first()
            info = ed.xpath('./div[2]/text()').extract_first()
            education_info['name'] = name
            try:
                education_info['name'] = name + " " + info.split("|")[0]
            except:
                pass
            try:
                education_info['info'] = info.split("|")[-1]
            except:
                pass
            education.append(education_info)
        i['education'] = education
        board_sertifications = []
        for board in response.xpath('//section[@data-qa-target="learn-certifications-section"]//ul/li'):
            board_sertifications_info = {}
            name = board.xpath('./div[1]/text()').extract_first()
            info = " ".join(board.xpath('./div[2]/span/text()').extract())
            board_sertifications_info['name'] = name
            try:
                board_sertifications_info['name'] = name
            except:
                pass
            try:
                board_sertifications_info['info'] = info
            except:
                pass
            board_sertifications.append(board_sertifications_info)
        i['board_sertifications'] = board_sertifications
        i['conditions_treated'] = response.xpath(
            '//section[@data-qa-target="learn-conditions-section"]//ul/li/text()').extract()
        i['office_address'] = response.meta['office_address']
        i['age'] = response.meta['age']
        i['full_name'] = response.meta['full_name']
        i['gender'] = response.meta['gender']
        i['midle_name'] = response.meta['midle_name']
        i['subspecialty'] = response.meta['subspecialty']
        i['office_name'] = response.xpath('//h3[@data-hgoname="summary-practice-name"]/text()')
        i['procedures'] = response.xpath('//div[@id="footer-section"]//a/@href').re('.+procedures.+')
        i['awards_and_recognition'] = response.xpath(
            '//section[@data-qa-target="learn-awards-section"]//h5/text()').extract()
        i['memberships'] = response.xpath('//section[@data-qa-target="learn-memberships-section"]//ul/li/text()').extract()
        i['languages_spoken'] = response.xpath('//section[@data-qa-target="learn-languages-section"]//ul/li/text()').extract()
        i['bio'] = response.xpath('//span[@class="learn-content"]/text()').extract_first()
        i['image_urls'] = response.meta['images']
        try:
            doctor_id = response.url.split('-')[-1].upper()
            post = yield scrapy.Request(
                method="POST",
                url='https://www.healthgrades.com/uisvc/v1_0/pesui/api/comments',
                headers={
                  'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
                    "Accept": "application/json",
                    "Content-Type":"application/json",
                    "Referer": response.url,
                    "Accept-Encoding": "gzip, deflate, br, json",
                },

                body=json.dumps({
                    'pwid': doctor_id,
                    'currentPage': '1',
                    'perPage': '500',
                    'sortOption': '1',
                })
            )

            reviews = []
            data = json.loads(post.body)
            for comento in data['results']:
                comment = {}
                comment['name'] = comento['displayName']
                comment['text'] = comento['commentText']
                comment['overallScore'] = str(comento['overallScore'])
                comment['submittedDate'] = comento['submittedDate']
                reviews.append(comment)
            i['reviews'] = reviews
        except:
            pass

        i['url'] = response.url
        i['first_name'] = response.meta['first_name']
        i['last_name'] = response.meta['last_name']
        i['specialty'] = response.meta['specialty']
        i['state'] = response.meta['state']
        insurances = []
        for n, div in enumerate(response.xpath('//*[@id="insurance-payor-list"]/li')):
            insurance = {}
            payor = div.xpath('.//div[@class="insurance-payor"]/text()').extract_first()
            for n2, div2 in enumerate(div.xpath('.//div[@class="insurance-plan"]/text()').extract()):
                insurance[payor] = div2
                insurances.append(insurance)
        i['insurances'] = insurances
        yield i