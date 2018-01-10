import scrapy
import json
from healthgrades.items import InsuranceItem


class InsuranceSpider(scrapy.Spider):
    name = "insurance_rt"
    custom_settings = {
        # 'ROBOTSTXT_OBEY': False
    }

    

    def parse(self, response):
        i = {}
        arguments = response.url.split('?')
        i['arguments'] = arguments[1:]
        arguments_dict = {}
        try:
            # uid = "58fc6bb51d70d0fbc2a2dfc64c22fd61"
            first_name = arguments_dict['name'].lower()
            last_name = arguments_dict['surname'].lower()
            city = arguments_dict['city']
            state = arguments_dict['state']
            # full_name = first_name + '%20' + last_name

        # state = 'NY'
        # city = 'NEW YORK'
        # first_name = 'DONALD'.lower()
        # last_name = 'SMITH'.lower()
            location = 'https://www.medicare.gov/geography/Geography.svc/LocationAutocompleteByZipRank/{},%20{}/ZP,CS/true'\
                .format(city, state)
            yield scrapy.Request(
                url=location,
                meta={
                    'first_name': first_name,
                    'last_name': last_name,
                    'city': city,
                    'state': state,
                },
                callback=self.location_medicare
            )
        except:
            pass

    def location_medicare(self, response):
        try:
            data = json.loads(response.body.decode())
        except:
            data = {}
        for d in data:
            lat = d.get('lat')
            lng = d.get('lng')
        url = 'https://www.medicare.gov/api/v1/providers/physician?filters[type]=ep&paging=1|1000&filters[proname]=Smith&lat={}&lng={}&dist=15&&prefix=y'.\
            format(lat, lng)
        yield scrapy.Request(
            url=url,
            meta={
                'first_name': response.meta.get('first_name'),
                'last_name': response.meta.get('last_name'),
                'city': response.meta.get('city'),
                'state': response.meta.get('state'),
            },
            callback=self.persons_medicare
        )

    def persons_medicare(self, response):
        'https://www.medicare.gov/api/v1/data/physician/specialtycrosswalk?locale=en'
        try:
            data = json.loads(response.body.decode())
        except:
            data = {}
        for person in data:
            if person.get('Name'):
                if person.get('Name').get('Last'):
                    first = person.get('Name').get('First').lower()
                    last = person.get('Name').get('Last').lower()
                    if response.meta.get('last_name') == last:
                        if response.meta.get('first_name') in first:
                            # print(person)
                            full_name = person.get('Name').get('FirstLast')
                            city = person.get('Addresses')[0].get('City')
                            state = person.get('Addresses')[0].get('State')
                            specialties = person.get('Addresses')[0].get('Specialties')
                            print(city, state, specialties)
                            return scrapy.Request(
                                url='https://www.medicare.gov/api/v1/data/physician/specialtycrosswalk?locale=en',
                                meta={
                                    'full_name': full_name,
                                    'first_name': first,
                                    'last_name': last,
                                    'city': city,
                                    'state': state,
                                    'specialties': specialties,
                                },
                                callback=self.parse_item_medicare
                            )

    def parse_item_medicare(self, response):
        i = InsuranceItem()
        a = {}
        data = json.loads(response.body.decode())
        for row in data:
            a[row.get('id')] = row.get('name')
        specialties = response.meta.get('specialties')
        all_spec = ''
        if specialties:
            for spec in specialties:
                if len(specialties) == 1:
                    all_spec = a.get(spec.get('_id'))
                elif len(specialties) >1:
                    all_spec =+ a.get(spec.get('_id')) + ', '

        i['full_name'] = response.meta.get('full_name').title()
        i['url'] = ''

        i['first_name'] = response.meta.get('first_name').title()
        i['last_name'] = response.meta.get('last_name').title()
        i['speciality'] = all_spec
        i['city'] = response.meta.get('city').title()
        i['state'] = response.meta.get('state')
        i['general_plan'] = ''
        i['plans'] = ''
        yield i