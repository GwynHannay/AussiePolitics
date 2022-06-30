import scrapy

class ActsSpider(scrapy.Spider):
    name = "acts"

    def start_requests(self):
        url = 'https://www.legislation.gov.au/Series/C2004A03898'
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        print('some text')
        print(response.css('title'))