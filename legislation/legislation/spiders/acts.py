import scrapy

class ActsSpider(scrapy.Spider):
    name = "acts"

    def start_requests(self):
        urls = ['https://www.legislation.gov.au/Browse/ByTitle/Acts/InForce/0/0/Principal']