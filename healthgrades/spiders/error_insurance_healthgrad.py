import scrapy
import json
import csv
import re


class InsuranceHealthgradSpider(scrapy.Spider):
    name = "error_insurance_healthgrad"
    output = []
    file = 'log_insurance_healthgrad_1.csv'
    with open(file, 'r') as lines:
        spamreader = csv.reader(lines)
        for line in spamreader:
            if 'ERROR' in line[1]:
                text = line[2]
                t = re.findall(r'<GET (.+)?>', text)
                output = output + t
    start_urls = output
    custom_settings ={
        'ROBOTSTXT_OBEY': False
    }


    def parse(self, response):
        page = json.loads(response.body.decode())
        for li in page['search']['searchResults']['provider']['results']:
            # print(li['providerUrl'])
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
                        # 'state': response.meta['state'],
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
        i['state'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
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