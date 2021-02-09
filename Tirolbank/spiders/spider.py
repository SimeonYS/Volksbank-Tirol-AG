import scrapy
from scrapy.loader import ItemLoader
from ..items import TirolbankItem
import re
from itemloaders.processors import TakeFirst

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'

class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.volksbank.tirol/private/news/']

    def parse(self, response):
        articles = response.xpath('//div[@class="column col-1-1-1-1"]')
        for article in articles:
            link = article.xpath('.//h3/a/@href').get()
            yield scrapy.Request(response.urljoin(link), callback=self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(TirolbankItem())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="column_padding article_block"]/h1/text()').get()
        content = response.xpath(
            '//div[@class="column_padding article_block"]//text()[not (ancestor::form) and not(ancestor::font)]').getall()
        content = ' '.join([text.strip() for text in content if text.strip()])
        content = re.sub(pattern, '', content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()