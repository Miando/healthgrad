import scrapy
from scrapy import Request, FormRequest
import json
import hashlib
from inline_requests import inline_requests
import os
import csv


class WwwSpider(scrapy.Spider):
    name = "healthgrad"
    start_urls = ['https://www.healthgrades.com/']
    custom_settings ={
        'ROBOTSTXT_OBEY': False
    }
    root_dir = os.path.abspath(os.path.dirname(__file__))

    def parse(self, response):
        files_list = os.listdir(self.root_dir )
        for f in files_list:
            if f[-1] == 'v':
                path = self.root_dir  + "/" +f

                with open(path, 'rb') as my_file:
                    reader = csv.reader(x.replace('\0', '') for x in my_file)
                    for n, row in enumerate(reader):
                        try:
                            uid = row[0]
                            first_name = row[1]
                            last_name = row[2]
                            title = row[3]
                            state = row[4]
                            full_name = first_name + '%20' + last_name
                            url = 'https://www.healthgrades.com/api3/usearch?userLocalTime=10:27&what={0}&where=NJ&state={1}&source=Solr&isStateOnly=true&sort.provider=bestmatch&categories=1&sessionId=S8739336cee27a5a2&requestId=R1696a9b870bbd8db&pageSize.provider=36&pageNum=1&isFirstRequest=true'.format(
                                full_name, state)
                            yield Request(
                                url=url,
                                meta={
                                    'uid':uid,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'title': title,
                                    'state': state,
                                },
                                callback=self.search_doctor
                            )
                        except:
                            pass
                    my_file.close()

    def search_doctor(self, response):
        i = {}
        page = json.loads(response.body)
        first_name = response.meta['first_name']
        last_name = response.meta['last_name']
        title = response.meta['title']
        state = response.meta['state']
        uid = response.meta['uid']
        duplicate = 0
        for li in page['search']['searchResults']['provider']['results']:
            name_data = li['displayName']
            url = 'https://www.healthgrades.com' + li['providerUrl']

            if first_name in name_data and last_name in name_data and title in name_data and state in li['displayOffice']['state']:

                status = 'OK'
                duplicate = duplicate + 1
                if duplicate > 1:
                    status = 'DUPLICATE'
                yield Request(
                    url=url,
                    meta={
                        'first_name': first_name,
                        'last_name': last_name,
                        'title': title,
                        'state': state,
                        'uid': uid,
                        'status': status,
                    },
                    callback=self.parse_item
                )
        if duplicate == 0:
            i['uid'] = response.meta['uid']
            i['status'] = 'NOTFOUND'
            i['first_name'] = response.meta['first_name']
            i['last_name'] = response.meta['last_name']
            i['title'] = response.meta['title']
            i['state'] = response.meta['state']
            yield i

    @inline_requests
    def parse_item(self, response):
        i = {}
        i['about'] = {}
        i['reviews'] = {}
        i['uid_new'] = hashlib.md5(response.url).hexdigest()
        i['uid'] = response.meta['uid']
        i['url'] = response.url
        i['status'] = response.meta['status']
        i['first_name'] = response.meta['first_name']
        i['last_name'] = response.meta['last_name']
        i['title'] = response.meta['title']
        i['state'] = response.meta['state']

        i['about']['patient_testimonials'] = response.xpath('//section[@data-qa-target="learn-testimonial-section"]/blockquote/span[2]/text()').extract()
        i['about']['care_philosophy'] = response.xpath('//section[@data-qa-target="learn-care-philosophy-section"]/blockquote/span[2]/text()').extract()
        i['about']['specialties'] = response.xpath('//section[@data-qa-target="learn-specialties-section"]//ul/li/text()').extract()
        i['about']['procedures'] = response.xpath('//section[@data-qa-target="learn-procedures-section"]//ul/li/text()').extract()
        i['about']['conditions_treated'] = response.xpath('//section[@data-qa-target="learn-conditions-section"]//ul/li/text()').extract()
        i['about']['languages_spoken'] = response.xpath('//section[@data-qa-target="learn-languages-section"]//ul/li/text()').extract()
        i['about']['memberships'] = response.xpath('//section[@data-qa-target="learn-memberships-section"]//ul/li/text()').extract()
        i['about']['board_sertifications'] = []
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
            i['about']['board_sertifications'].append(board_sertifications_info)
        i['about']['education'] = []
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
            i['about']['education'].append(education_info)
        i['about']['awards_and_recognition'] = response.xpath('//section[@data-qa-target="learn-awards-section"]//h5/text()').extract()

        i['reviews']['likelihood_rate'] = response.xpath('//div[@class="summary-stars"]/span[@class="rating-value"]/text()').extract_first()
        i['reviews']['total_reviews'] = response.xpath('//div[@class="score-details"]/span[@class="number"]/text()').extract_first()
        i['reviews']['reviews_with_comments'] = response.xpath('//div[@class="score-details"]/span/span[@class="number"]/text()').extract_first()
        try:
            doctor_id = response.url.split('-')[-1].upper()
            post = yield Request(
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

            i['reviews']['comments'] = []
            data = json.loads(post.body)
            for comento in data['results']:
                comment = {}
                comment['name'] = comento['displayName']
                comment['text'] = comento['commentText']
                comment['overallScore'] = str(comento['overallScore'])
                comment['submittedDate'] = comento['submittedDate']
                i['reviews']['comments'].append(comment)
        except:
            pass
        for li in response.xpath('//ul[@class="hg-survey-aggregate-group"]/li'):
            name = li.xpath('.//div[@class="title"]/text()').extract_first()
            value = li.xpath('.//span[@class="review-bar-text"]/text()').extract_first()
            i['reviews'][name] = value
        yield i