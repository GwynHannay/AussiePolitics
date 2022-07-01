import scrapy

class ActsSpider(scrapy.Spider):
    name = "acts"
    start_urls = ['https://www.legislation.gov.au/Series/C2004A03898']
    download_delay = 0.5
    
    def parse(self, response, **cb_kwargs):
        print(response.css('title'))
        href = response.css('.rgPagerCell').xpath('.//a')
        if cb_kwargs.get('visited'):
            kwargs = cb_kwargs
        else:
            kwargs = {'visited': []}
        event_target = None
        print(kwargs)

        for link in href:
            js_function = link.xpath('./@href').get()
            if not js_function:
                break
            
            if js_function not in kwargs['visited']:
                if link.xpath('./@class'):
                    kwargs['visited'].append(js_function)
                    continue
                else:
                    event_target = js_function.replace("javascript:__doPostBack('", "").replace("','')", "")
                    print(event_target)
                    kwargs['visited'].append(js_function)
                    break

        event_argument = response.css('#__EVENTARGUMENT::attr(value)').extract()
        last_focus = response.css('#__LASTFOCUS::attr(value)').extract()
        view_state = response.css('#__VIEWSTATE::attr(value)').extract()
        view_state_generator = response.css('#__VIEWSTATEGENERATOR::attr(value)').extract()
        view_state_encrypted = response.css('#__VIEWSTATEENCRYPTED::attr(value)').extract()

        rows = response.css('.rgMasterTable').xpath('./tbody/tr')
        for row in rows:
            print(row.xpath('./td/table//@href').get())

        if event_target:
            yield scrapy.FormRequest(
                'https://www.legislation.gov.au/Series/C2004A03898',
                formdata={
                    '__EVENTTARGET': event_target,
                    '__EVENTARGUMENT': event_argument,
                    '__LASTFOCUS': last_focus,
                    '__VIEWSTATE': view_state,
                    '__VIEWSTATEGENERATOR': view_state_generator,
                    '__VIEWSTATEENCRYPTED': view_state_encrypted
                },
                callback=self.parse,
                cb_kwargs=kwargs
            )
    
    def page_me(self, response):
        print(response.css('title'))
        print(response.css('.rgPagerCell').xpath('.//a').getall())