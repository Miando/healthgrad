# import scrapy
# from healthgrades.items import InsuranceItem
# from nameparser import HumanName
# from w3lib.html import remove_tags
#
#
# class UnitedHealthCareSpider(scrapy.Spider):
#     name = "united_health_care"
#     start_urls = ['https://connect.werally.com/plans/uhc/1']
#     # custom_settings ={
#     #     'ROBOTSTXT_OBEY': False
#     # }
#
#     def parse(self, response):
#         options = response.xpath('//h3[@class="list-title"]/a')
#         for option in options:
#             yield scrapy.Request(
#                 url='https://connect.werally.com{}'
#                     .format(option.xpath('./@href').extract_first()),
#                 meta={
#                     'plane': option.xpath('./text()').extract_first(),
#                 },
#                 callback=self.parse_plane
#             )
#
#     def parse_plane(self, response):
#         links = response.xpath('//td[@class="opd-name-list"]/a/@href').extract()
#         for link in links:
#             yield scrapy.Request(
#                 url='http://doctorfinder.horizonblue.com{}'.format(link),
#                 meta={
#                     'state': response.meta.get('state'),
#                     'plane': response.meta.get('plane'),
#                 },
#                 callback=self.parse_item
#             )
#         next_p = response.xpath('//li[@class="next"]/a/@href').extract_first()
#         if next_p:
#             yield scrapy.Request(
#                 url='http://doctorfinder.horizonblue.com{}'.format(next_p),
#                 meta={
#                     'state': response.meta.get('state'),
#                     'plane': response.meta.get('plane'),
#                 },
#                 callback=self.parse_table
#             )
#
#     def parse_item(self, response):
#         i = InsuranceItem()
#         full_name = remove_tags(response.xpath('//h3[@class="media-heading profile-heading"]')
#                                 .extract_first(default=''))
#         i['full_name'] = full_name
#         i['url'] = response.url
#         if full_name:
#             name = HumanName(full_name)
#             i['first_name'] = name.first
#             i['last_name'] = name.last
#         i['speciality'] = response.xpath('//h4[@class="media-subheading"]/a/text()').extract_first(default='')
#         i['city'] = response.xpath('//div[@class="row profile-address"]/div/h4/text()').re_first('(.+?),')
#         i['state'] = response.meta.get('state')
#         i['general_plan'] = response.meta.get('plane')
#         i['plans'] = response.xpath('//span[@id="plans_accepted"]//p[@class="text-success"]/text()').re('\S.+')
#         yield i
