# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from tripadvisor_scraping.items import UserReviewItem


class DefaultValuesPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, UserReviewItem):
            item.setdefault('review_helpful_vote', 0)
            return item

        return item
