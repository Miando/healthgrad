import scrapy
import json
from healthgrades.items import InsuranceItem


class InsuranceHealthgradSpider(scrapy.Spider):
    name = "insurance_healthgrad"
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
                    name = li['displayName']
                    if 'Dr.' in name:
                        name = name.replace('Dr. ', '')
                    first_name = name.split(' ')[0]
                    last_name = name.replace(first_name + ' ', '')
                    if ',' in name:
                        last_name = last_name.split(',')[0]
                    specialty = li['specialty']
                    yield scrapy.Request(
                        url='https://www.healthgrades.com' + li['providerUrl'],
                        meta={
                            'first_name': first_name,
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
                name = li['displayName']
                if 'Dr.' in name:
                    name = name.replace('Dr. ', '')
                first_name = name.split(' ')[0]
                last_name = name.replace(first_name + ' ', '')
                if ',' in name:
                    last_name = last_name.split(',')[0]
                specialty = li['specialty']
                yield scrapy.Request(
                    url='https://www.healthgrades.com' + li['providerUrl'],
                    meta={
                        'first_name': first_name,
                        'last_name': last_name,
                        'specialty': specialty,
                        'state': response.meta['state'],
                    },
                    callback=self.parse_item
                )
            except:
                pass

    def parse_item(self, response):
        i = {}

        i['first_name'] = response.meta['first_name']
        i['last_name'] = response.meta['last_name']
        i['specialty'] = response.meta['specialty']
        i['state'] = response.meta['state']
        for n, div in enumerate(response.xpath('//*[@id="insurance-payor-list"]/li')):
            i['payor{}'.format(str(n+1))] = div.xpath('.//div[@class="insurance-payor"]/text()').extract_first()
            for n2, div2 in enumerate(div.xpath('.//div[@class="insurance-plan"]/text()').extract()):
                i['payor{}_plan{}'.format(str(n+1), str(n2+1))] = div2
        # i['about']['patient_testimonials'] = response.xpath('//section[@data-qa-target="learn-testimonial-section"]/blockquote/span[2]/text()').extract()
        # i['about']['care_philosophy'] = response.xpath('//section[@data-qa-target="learn-care-philosophy-section"]/blockquote/span[2]/text()').extract()
        # i['about']['specialties'] = response.xpath('//section[@data-qa-target="learn-specialties-section"]//ul/li/text()').extract()
        # i['about']['procedures'] = response.xpath('//section[@data-qa-target="learn-procedures-section"]//ul/li/text()').extract()
        # i['about']['conditions_treated'] = response.xpath('//section[@data-qa-target="learn-conditions-section"]//ul/li/text()').extract()
        # i['about']['languages_spoken'] = response.xpath('//section[@data-qa-target="learn-languages-section"]//ul/li/text()').extract()
        # i['about']['memberships'] = response.xpath('//section[@data-qa-target="learn-memberships-section"]//ul/li/text()').extract()
        # i['about']['board_sertifications'] = []
        # for board in response.xpath('//section[@data-qa-target="learn-certifications-section"]//ul/li'):
        #     board_sertifications_info = {}
        #     name = board.xpath('./div[1]/text()').extract_first()
        #     info = " ".join(board.xpath('./div[2]/span/text()').extract())
        #     board_sertifications_info['name'] = name
        #     try:
        #         board_sertifications_info['name'] = name
        #     except:
        #         pass
        #     try:
        #         board_sertifications_info['info'] = info
        #     except:
        #         pass
        #     i['about']['board_sertifications'].append(board_sertifications_info)
        # i['about']['education'] = []
        # for ed in response.xpath('//section[@data-qa-target="learn-education-section"]//ul/li'):
        #     education_info = {}
        #     name = ed.xpath('./div[1]/text()').extract_first()
        #     info = ed.xpath('./div[2]/text()').extract_first()
        #     education_info['name'] = name
        #     try:
        #         education_info['name'] = name + " " + info.split("|")[0]
        #     except:
        #         pass
        #     try:
        #         education_info['info'] = info.split("|")[-1]
        #     except:
        #         pass
        #     i['about']['education'].append(education_info)
        # i['about']['awards_and_recognition'] = response.xpath('//section[@data-qa-target="learn-awards-section"]//h5/text()').extract()
        #
        # i['reviews']['likelihood_rate'] = response.xpath('//div[@class="summary-stars"]/span[@class="rating-value"]/text()').extract_first()
        # i['reviews']['total_reviews'] = response.xpath('//div[@class="score-details"]/span[@class="number"]/text()').extract_first()
        # i['reviews']['reviews_with_comments'] = response.xpath('//div[@class="score-details"]/span/span[@class="number"]/text()').extract_first()
        # try:
        #     doctor_id = response.url.split('-')[-1].upper()
        #     post = yield Request(
        #         method="POST",
        #         url='https://www.healthgrades.com/uisvc/v1_0/pesui/api/comments',
        #         headers={
        #           'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
        #             "Accept": "application/json",
        #             "Content-Type":"application/json",
        #             "Referer": response.url,
        #             "Accept-Encoding": "gzip, deflate, br, json",
        #         },
        #
        #         body=json.dumps({
        #             'pwid': doctor_id,
        #             'currentPage': '1',
        #             'perPage': '500',
        #             'sortOption': '1',
        #         })
        #     )
        #
        #     i['reviews']['comments'] = []
        #     data = json.loads(post.body)
        #     for comento in data['results']:
        #         comment = {}
        #         comment['name'] = comento['displayName']
        #         comment['text'] = comento['commentText']
        #         comment['overallScore'] = str(comento['overallScore'])
        #         comment['submittedDate'] = comento['submittedDate']
        #         i['reviews']['comments'].append(comment)
        # except:
        #     pass
        # for li in response.xpath('//ul[@class="hg-survey-aggregate-group"]/li'):
        #     name = li.xpath('.//div[@class="title"]/text()').extract_first()
        #     value = li.xpath('.//span[@class="review-bar-text"]/text()').extract_first()
        #     i['reviews'][name] = value
        yield i