import scrapy
import json
from healthgrades.items import InsuranceItem
import MySQLdb as dbapi


class InsuranceSpider(scrapy.Spider):
    name = "insurance_rt"
    custom_settings = {
        # 'ROBOTSTXT_OBEY': False
    }


    def parse(self, response):
        i = {}
        # print(response.url.split('?'))
        arguments = response.url.split('?')
        i['arguments'] = arguments[1:]
        arguments_dict = {}
        for argument in arguments[1:]:
            args = argument.split('=')
            arguments_dict[args[0]] = args[1]

        yield i


        # try:
            # uid = "58fc6bb51d70d0fbc2a2dfc64c22fd61"
        first_name = arguments_dict.get('name').lower()
        last_name = arguments_dict.get('surname').lower()
        city = arguments_dict.get('city')
        state = arguments_dict.get('state')

        location = 'https://www.medicare.gov/geography/Geography.svc/LocationAutocompleteByZipRank/{}, {}/ZP,CS/false' \
            .format(city, state)
        if city:
            city = city.replace('%20', '')
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
        # full_name = first_name + '%20' + last_name
        dbServer = '159.89.39.167'
        dbPass = '&/rDGW,GHv?fFCM{3HnG'
        dbSchema = 'health'
        dbUser = 'root'
        spider_names = ['amerihealth', 'horizonblue', '1199']
        for s in spider_names:
            print(s)
            dbQuery = "SELECT * FROM  health.data WHERE spider_name = '{}' AND lower(first_name) ='{}' AND lower(last_name) ='{}' AND lower(state) ='{}';".format(
                s, first_name.lower(), last_name.lower(), state.lower())
            # dbQuery = "SELECT * FROM  health.data WHERE spider_name = '{}' AND lower(first_name) ='{}';".format(
            #     s, first_name.lower())
            db = dbapi.connect(host=dbServer, user=dbUser, passwd=dbPass)
            cur = db.cursor()
            cur.execute(dbQuery)
            results = cur.fetchall()
            if results:
                p = {}
                pp = []
                result=results[0]

                p={}
                p['full_name'] = result[1]
                p['url'] = result[2]

                p['first_name'] = result[3]
                p['last_name'] = result[4]
                p['speciality'] = result[5]
                p['city'] = result[6]
                p['state'] = result[7]
                p['general_plan'] = result[8]
                p['plans'] = result[9]
                p['spider_name'] = result[10]

            else:
                p = {}
                p['result'] = 'no insurance'
                p['spider_name'] = s
            yield p

    # state = 'NY'
    # city = 'NEW YORK'
    # first_name = 'DONALD'.lower()
    # last_name = 'SMITH'.lower()

        # except:
        #     pass

    # def get_from_db(self, first_name, last_name, city, state):



    def location_medicare(self, response):
        try:
            data = json.loads(response.body.decode())
        except:
            data = {}
        lat = ''
        lng = ''
        for d in data:
            lat = d.get('lat')
            lng = d.get('lng')
            break
        url = 'https://www.medicare.gov/api/v1/providers/physician?filters[type]=ep&paging=1|200&filters[proname]={}&lat={}&lng={}&dist=15&&prefix=y'. \
            format(response.meta.get('last_name').lower(), lat, lng)
        print (url)
        # url = 'https://www.medicare.gov/api/v1/providers/physician?filters[type]=ep&paging=1|200&filters[proname]=smith&lat=40.7143528&lng=-74.0059731&dist=15&&prefix=y'.\

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
        print(data)
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
        data = json.loads(response.body.decode('ascii', 'ignore'))
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