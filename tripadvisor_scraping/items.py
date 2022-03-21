# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
import re


# Convert month text to digit
def month_to_digit(month):
    match month:
        case "Jan.":
            return "1"
        case "Feb.":
            return "2"
        case "März":
            return "3"
        case "Apr.":
            return "4"
        case "Mai":
            return "5"
        case "Juni":
            return "6"
        case "Juli":
            return "7"
        case "Aug.":
            return "8"
        case "Sep.":
            return "9"
        case "Okt.":
            return "10"
        case "Nov.":
            return "11"
        case "Dez.":
            return "12"


# Extract the date out of the string
def extract_review_date(text):
    date = text.replace(' hat im ', '').replace('eine Bewertung geschrieben.', '')
    if date[0].isdigit():
        date = re.sub(r'[0-9+]', '', date).replace('. ', '')
        date = month_to_digit(date)
        date = str(date) + ' 2022'
    else:
        year = date[-5:]
        month = date[:-5]
        date = str(month_to_digit(month)) + " " + str(year)

    return date


# Score is a class like bubble_45 for 4.5, just return the score
def extract_hotel_score(text):
    score = text.replace('ui_bubble_rating ', '')
    return float(score[-2:]) / 10


# Score is a class like bubble_50 for 5, just return the score
def extract_review_score(text):
    return int(text.replace('ui_bubble_rating ', '')[-2])


def remove_whitespace(text):
    return text.strip()


class HotelItem(scrapy.Item):
    hotel_id = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    hotel_name = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace), output_processor=TakeFirst())
    hotel_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_hotel_score), output_processor=TakeFirst())


class HotelReviewItem(scrapy.Item):
    # hotel_id = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    # hotel_name = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace), output_processor=TakeFirst())
    review_id = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    username = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    review_helpful_vote = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst()) # TODO Need to get the second element
    review_date = scrapy.Field(input_processor=MapCompose(remove_tags, extract_review_date), output_processor=TakeFirst())
    review_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_review_score), output_processor=TakeFirst())
    review_title = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    review_text = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())


class UserReviewItem(scrapy.Item):
    pass

