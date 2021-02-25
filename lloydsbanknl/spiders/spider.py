import scrapy

from scrapy.loader import ItemLoader
from ..items import LloydsbanknlItem
from itemloaders.processors import TakeFirst


class LloydsbanknlSpider(scrapy.Spider):
	name = 'lloydsbanknl'
	start_urls = ['https://www.lloydsbank.nl/nieuws']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news-items__item__text"]')
		for post in post_links:
			url = post.xpath('./a/@href').get()
			date = post.xpath('./div[@class="time"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//div[@class="pagination"]//a/@href').getall()
		yield from response.follow_all(next_page, self.parse)


	def parse_post(self, response, date):
		title = response.xpath('//div[@class="header__content"]/h1/text()').get()
		description = response.xpath('//main/div[@class="container"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=LloydsbanknlItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
