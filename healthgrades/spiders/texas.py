import scrapy
import string

class TexasSpider(scrapy.Spider):
    name = "texas"
    start_urls = ['https://public.tmb.state.tx.us/HCP_Search/SearchInput.aspx']
    custom_settings ={
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': False,
        # 'REDIRECT_MAX_TIMES': 2
    }
    # handle_httpstatus_list = [500]

    def parse(self, response):
        yield scrapy.FormRequest(
            url='https://public.tmb.state.tx.us/HCP_Search/SearchNotice.aspx',
            formdata={
                '__VIEWSTATE': response.xpath(
                    '//*[@id="__VIEWSTATE"]/@value').extract_first(default=''),
                '__VIEWSTATEGENERATOR': response.xpath(
                    '//*[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(default=''),
                '__EVENTVALIDATION': response.xpath(
                    '//*[@id="__EVENTVALIDATION"]/@value').extract_first(default=''),
                'ctl00$BodyContent$btnAccept': 'I+Accept+the+Usage+Terms',
            },

            callback=self.next1
        )

    def next1(self, response):
        licensies = response.xpath('//*[@id="BodyContent_ddLicenseType"]/option/@value').extract()
        print(licensies)
        alpfabet = string.ascii_lowercase
        for a in alpfabet:
            for l in licensies:
                if l != "ALL":
                    yield scrapy.Request(
                        url='https://public.tmb.state.tx.us/HCP_Search/SearchResults.aspx?LN={}*&LT={}'.format(a, l),

                        # headers={
                        #     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
                        # },
                        meta={'a': a, 'l': l},
                        callback=self.next2
                    )
                    break
            break

    def next2(self, response):
        urls = response.xpath('//a/@href').re("ctl00\$BodyContent\$gvSearchResults\$ctl\d{2}\$ctl00")
        for url in urls:
            yield scrapy.FormRequest(
                url='https://public.tmb.state.tx.us/HCP_Search/SearchResults.aspx?LN={}*&LT={}'\
                    .format(response.meta.get('a'), response.meta.get('l')),
                formdata={
                    '__VIEWSTATE': response.xpath(
                        '//*[@id="__VIEWSTATE"]/@value').extract_first(default=''),
                    'ctl00$BodyContent$hfSQLDebug': response.xpath(
                        '//*[@id="BodyContent_hfSQLDebug"]/@value').extract_first(default=''),
                    '__VIEWSTATEGENERATOR': response.xpath(
                        '//*[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(default=''),
                    '__EVENTVALIDATION': response.xpath(
                        '//*[@id="__EVENTVALIDATION"]/@value').extract_first(default=''),
                    '__EVENTTARGET': url,
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br'
                },
                # meta={'dont_redirect': True, "handle_httpstatus_list": [302]},
                callback=self.next3
            )
            # break

    def next3(self, response):
        print(response.meta.get('redirect_urls'))
        # print(response.body)
        i = {}
        i['NAME'] = response.xpath('//strong[contains(text(), "NAME:")]/../../text()').extract_first(default='')
        i['Date of Birth'] = response.xpath('//strong[contains(text(), "Date of Birth:")]/../text()').extract_first(
            default='')
        i['TMB License Number'] = response.xpath('//strong[contains(text(), "TMB License Number:")]/../text()').extract_first(
            default='')
        i['DSHS License Number'] = response.xpath('//strong[contains(text(), "DSHS License Number:")]/../text()').extract_first(
            default='')
        i['Issuance Date'] = response.xpath('//strong[contains(text(), "Issuance Date:")]/../text()').extract_first(
            default='')
        i['Expiration Date'] = response.xpath('//strong[contains(text(), "Expiration Date:")]/../text()').extract_first(
            default='')
        i['Registration Status'] = response.xpath('//strong[contains(text(), "Registration Status:")]/../text()').extract_first(
            default='')
        i['Registration Date'] = response.xpath('//strong[contains(text(), "Registration Date:")]/../text()').extract_first(
            default='')
        i['Disciplinary Status'] = response.xpath('//strong[contains(text(), "Disciplinary Status:")]/../text()').extract_first(
            default='')
        i['Disciplinary Date'] = response.xpath('//strong[contains(text(), "Disciplinary Date:")]/../text()').extract_first(
            default='')
        i['Licensure Status'] = response.xpath('//strong[contains(text(), "Licensure Status:")]/../text()').extract_first(
            default='')
        i['Mailing Address'] = response.xpath('//strong[contains(text(), "Mailing Address")]/../text()').extract_first(
            default='')
        i['Board Action'] = response.xpath('//strong[contains(text(), "Board Action")]/../text()').extract_first(
            default='')
        i['Gender'] = response.xpath('//strong[contains(text(), "Gender")]/../text()').extract_first(
            default='')
        i['Current Primary Practice Address'] = response.xpath('//strong[contains(text(), "Current Primary Practice Address")]/../text()').extract_first(
            default='')
        yield i
        yield scrapy.Request(
            url=response.meta.get('redirect_urls')[1],
            dont_filter=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
            },
            callback=self.next4
        )

    def next4(self, response):
        pass