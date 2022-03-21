# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
import re


# Extract the date out of the string
def extract_review_date(text):
    date = text.replace(' hat im ', '').replace('eine Bewertung geschrieben.', '')
    if date[0].isdigit():
        date = re.sub(r'[0-9+]', '', date).replace('. ', '')
        date = date + '2022'

    return date


# Score is a class like bubble_50 for 5, just return the score
def extract_review_score(text):
    return int(text.replace('ui_bubble_rating ', '')[-2])


class HotelReviewItem(scrapy.Item):
    # define the fields for your item here like:
    username = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    review_helpful_vote = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst()) # TODO Need to get the second element
    review_date = scrapy.Field(input_processor=MapCompose(remove_tags, extract_review_date), output_processor=TakeFirst())
    review_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_review_score), output_processor=TakeFirst())
    review_id = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    review_title = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    review_text = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())

