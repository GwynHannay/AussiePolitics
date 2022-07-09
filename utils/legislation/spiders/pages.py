import scrapy
from scrapy.http import Request


class PagesSpider(scrapy.Spider):
    name = "pages"

    def __init__(self, **kw):
        """Receives the URL to page through.

        Raises:
            Exception: If no URL was passed.
        """        
        super(PagesSpider, self).__init__(**kw)
        self.url = kw.get('url') or kw.get('domain') or 'dummy'
        if self.url == 'dummy':
            raise Exception('No URL was passed to the pages spider, only: {}'.format(kw))

    def start_requests(self):   
        return [Request(self.url, callback=self.parse)]

    def parse(self, response, **cb_kwargs):
        href = response.css('.rgPagerCell').xpath('.//a')
        if cb_kwargs.get('visited'):
            kwargs = cb_kwargs
        else:
            kwargs = {'visited': []}
        event_target = None

        for link in href:
            js_function = link.xpath('./@href').get()
            if not js_function:
                break

            if js_function not in kwargs['visited']:
                if link.xpath('./@class'):
                    kwargs['visited'].append(js_function)
                    continue
                else:
                    event_target = js_function.replace(
                        "javascript:__doPostBack('", "").replace("','')", "")
                    kwargs['visited'].append(js_function)
                    break

        event_argument = response.css(
            '#__EVENTARGUMENT::attr(value)').extract()
        last_focus = response.css('#__LASTFOCUS::attr(value)').extract()
        view_state = response.css('#__VIEWSTATE::attr(value)').extract()
        view_state_generator = response.css(
            '#__VIEWSTATEGENERATOR::attr(value)').extract()
        view_state_encrypted = response.css(
            '#__VIEWSTATEENCRYPTED::attr(value)').extract()

        rows = response.css('.rgMasterTable').xpath('./tbody/tr')
        for row in rows:
            yield {
                'canonical_link': self.url,
                'series_link': row.xpath('./td/table//@href').get()
            }

        if event_target:
            yield scrapy.FormRequest(
                self.url,
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
