import scrapy
import csv

class FoksSpider(scrapy.Spider):
    name = 'foks'
    start_urls = ['https://foks-donetsk.com/']
    
    def parse(self, response):
        all_categories = response.xpath('//a[@class="all-cat-menu-link"]/@href')
        for category in all_categories:
            yield response.follow(category, self.parse_category)
            
    def parse_category(self, response):
        for product in response.css('div.catalog_item_name a::attr("href")'):
            yield response.follow(product, self.parse_product)
        next_page = response.css('a.pagination-item-arrow_right::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse_category)
            
    def parse_product(self, response):
        name = response.css('div.product-item h1::text').get().strip()
        category = response.css('div.product_header a::text').get().strip()
        price = response.css('div.product_info_price span::text').get().strip()
        link = response.url
        
        yield {
            'Name': name,
            'Category': category,
            'Price': price,
            'Link': link
        }

class FoksPipeline:
    def __init__(self):
        super().__init__()  # добавляем вызов родительской инициализации
        self.file = open('foks.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=['Name', 'Category', 'Price', 'Link'])
        self.writer.writeheader()
        
    def process_item(self, item, spider):
        self.writer.writerow(item)
        return item
    
    def close_spider(self, spider):
        self.file.close()