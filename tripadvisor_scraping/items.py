# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags
import re


# Convert month text to digit
def month_to_digit(month):
    """
    Given a month, return the digit of the month

    >>> month_to_digit('Februar')
    '2'

    >>> month_to_digit('Sept.')
    '9'
    """
    match month:
        case "Jan." | 'Januar':
            return "1"
        case "Feb." | 'Februar':
            return "2"
        case "März":
            return "3"
        case "Apr." | 'April':
            return "4"
        case "Mai":
            return "5"
        case "Juni":
            return "6"
        case "Juli":
            return "7"
        case "Aug." | 'August':
            return "8"
        case "Sept." | 'September':
            return "9"
        case "Okt." | 'Oktober':
            return "10"
        case "Nov." | 'November':
            return "11"
        case "Dez." | 'Dezember':
            return "12"


def extract_review_date(review_date):
    """
    Extract the date out of the review date

    :param review_date: str
    :return: str with day, month and year

    >>> extract_review_date('29. Juni 2011')
    '29.6.2011'

    >>> extract_review_date('6. März 2019')
    '6.3.2019'
    """
    day = re.findall('^[0-9]+', review_date)[0]
    month = re.findall('[A-Z][a-z]+|März', review_date)[0]
    year = re.findall('[0-9]{4}', review_date)[0]

    return str(day) + '.' + str(month_to_digit(month)) + "." + str(year)


def extract_date_of_stay(date_of_stay):
    """
    Extract the date out of the date of stay string

    :param date_of_stay: str
    :return: str with month and year

    >>> extract_date_of_stay(' September 2020')
    '9.2020'
    """
    date = date_of_stay[1:]
    year = date[-4:]
    month = date[:-5]

    return str(month_to_digit(month)) + '.' + str(year)


def extract_score(score_class):
    """
    Extract the score out of the class bubble

    :param score_class: str
    :return: score: float

    >>> extract_score('ui_bubble_rating bubble_50')
    5.0

    >>> extract_score('ui_bubble_rating bubble_35')
    3.5
    """
    score = score_class.replace('ui_bubble_rating ', '')
    return float(score[-2:]) / 10


def remove_unnecessary_whitespace(text):
    """
    Removes any leading spaces at the beginning and trailing spaces at the end

    :param text: str
    :return: text: str

    >>> remove_unnecessary_whitespace('       Hotel Murtenhof & Krone  ')
    'Hotel Murtenhof & Krone'
    """
    return text.strip()


def extract_review_id(review_link):
    """
    Extract review id from review link

    :param review_link: str
    :return: review_id: str

    >>> extract_review_id('/ShowUserReviews-g910519-d627041-r801898967-Hotel_Murtenhof_Krone-Murten_Canton_of_Fribourg.html')
    '801898967'

    >>> extract_review_id('/Hotel_Review-g293891-d1513579-Reviews-Hotel_Crown-Pokhara_Gandaki_Zone_Western_Region.html')
    '/Hotel_Review-g293891-d1513579-Reviews-Hotel_Crown-Pokhara_Gandaki_Zone_Western_Region.html'

    >>> extract_review_id('/ShowUserReviews-g198829-d253607-r29693415-Hotel_Krone_Hotel_de_la_Couronne-Meyriez_Canton_of_Fribourg.html')
    '29693415'
    """
    if '/ShowUserReviews' in review_link:
        return re.findall('-r[0-9]{7,10}-', review_link)[0][2:-1]
    else:
        return review_link


def extract_user_review_helpful_vote(helpful_vote):
    """
    Extract the number of helpful vote on user review page

    :param helpful_vote: str
    :return: number: int

    >>> extract_user_review_helpful_vote('1 \xa0')
    1
    """
    return int(helpful_vote[0])


def extract_hotel_id(review_link):
    """
    Extract the hotel id from review link

    :param review_link: str
    :return: hotel_id: str

    >>> extract_hotel_id('/ShowUserReviews-g910519-d627041-r801898967-Hotel_Murtenhof_Krone-Murten_Canton_of_Fribourg.html')
    '627041'

    >>> extract_hotel_id('/Hotel_Review-g910519-d19778035-Reviews-Zimmerei-Murten_Canton_of_Fribourg.html')
    '19778035'
    """
    return re.findall('-d[0-9]+-', review_link)[0][2:-1]


class HotelItem(scrapy.Item):
    hotel_id = scrapy.Field(input_processor=MapCompose(remove_tags, extract_hotel_id),
                            output_processor=TakeFirst())
    hotel_name = scrapy.Field(input_processor=MapCompose(remove_tags, remove_unnecessary_whitespace),
                              output_processor=TakeFirst())
    hotel_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_score),
                               output_processor=TakeFirst())


class HotelIdReviewIdItem(scrapy.Item):
    hotel_id = scrapy.Field(input_processor=MapCompose(remove_tags, extract_hotel_id),
                            output_processor=TakeFirst())
    review_id = scrapy.Field(input_processor=MapCompose(remove_tags, extract_review_id),
                             output_processor=TakeFirst())


class UserReviewItem(scrapy.Item):
    username_id = scrapy.Field(input_processor=MapCompose(remove_tags),
                               output_processor=TakeFirst())
    review_id = scrapy.Field(input_processor=MapCompose(remove_tags),
                             output_processor=TakeFirst())
    review_helpful_vote = scrapy.Field(input_processor=MapCompose(remove_tags, extract_user_review_helpful_vote),
                                       output_processor=TakeFirst())
    review_date = scrapy.Field(input_processor=MapCompose(remove_tags, extract_review_date),
                               output_processor=TakeFirst())
    date_of_stay = scrapy.Field(input_processor=MapCompose(remove_tags, extract_date_of_stay),
                                output_processor=TakeFirst())
    review_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_score),
                                output_processor=TakeFirst())
    review_title = scrapy.Field(input_processor=MapCompose(remove_tags),
                                output_processor=TakeFirst())
    review_text = scrapy.Field(input_processor=MapCompose(remove_tags),
                               output_processor=TakeFirst())
