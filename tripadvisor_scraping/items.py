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
    Extract the date out of the review date string

    :param review_date: str
    :return: str with month and year

    >>> extract_review_date(' hat im Juni 2019 eine Bewertung geschrieben.')
    '6 2019'

    Seems not to exists anymore
    >>> extract_review_date(' hat im 3. März eine Bewertung geschrieben.')
    '3 2022'

    >>> extract_review_date('Sept. 2019')
    '9 2019'

    Seems not to exists anymore
    >>> extract_review_date('18. März')
    '3 2022'

    >>> extract_review_date('18. März')
    '3 2022'
    """
    date = review_date.replace(' hat im ', '').replace(' eine Bewertung geschrieben.', '')
    if date[0].isdigit():
        date = re.sub(r'[0-9+]', '', date).replace('. ', '')
        date = month_to_digit(date)
        date = str(date) + ' 2022'
    else:
        year = date[-4:]
        month = date[:-5]
        date = str(month_to_digit(month)) + " " + str(year)

    return date


def extract_date_of_stay_review(date_of_stay):
    """
    Extract the date out of the date of stay string

    :param date_of_stay: str
    :return: str with month and year

    >>> extract_date_of_stay_review(' September 2020')
    '9 2020'
    """
    date = date_of_stay[1:]
    year = date[-5:]
    month = date[:-5]

    return str(month_to_digit(month)) + str(year)

def extract_date_of_stay(date_of_stay):
    """
    Extract the date out of the date of stay string

    :param date_of_stay: str
    :return: str with month and year

    >>> extract_date_of_stay(' August 2017 September 2017 August 2017 Juli 2017 Juli 2017 Oktober 2016')
    '8 2017'
    """
    date = re.findall("^\s[A-Z][a-zA-Z]+\s[0-9]+", date_of_stay)[0]
    month = date[1:-5]
    year = date[-4:]
    date = str(month_to_digit(month)) + " " + str(year)

    return date

# TODO Funktionert nicht wie gewünscht
def extract_date_of_stay_array(date_of_stay):
    """
    Extract the date out of the date of stay array

    :param date_of_stay: str
    :return: str with month and year

    >>> extract_date_of_stay_array([' Oktober 2021', ' Oktober 2021', ' September 2021', ' September 2020', ' März 2020', ' Februar 2020'])
    '10 2021'
    """
    date = date_of_stay[0][1:]
    month = date[:-5]
    year = date[-4:]
    date = str(month_to_digit(month)) + " " + str(year)

    return date

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


def extract_username_id(profile_link):
    """
    Extract the real username from the profile link

    :param profile_link: str
    :return: username_id: str

    >>> extract_username_id('/Profile/Geniessender')
    'Geniessender'
    """
    return profile_link.replace('/Profile/', '')


def extract_review_id(review_link):
    """
    Extract review id from review link

    :param review_link: str
    :return: review_id: str

    >>> extract_review_id('/ShowUserReviews-g910519-d627041-r801898967-Hotel_Murtenhof_Krone-Murten_Canton_of_Fribourg.html')
    '801898967'

    >>> extract_review_id('/Hotel_Review-g293891-d1513579-Reviews-Hotel_Crown-Pokhara_Gandaki_Zone_Western_Region.html')
    '/Hotel_Review-g293891-d1513579-Reviews-Hotel_Crown-Pokhara_Gandaki_Zone_Western_Region.html'
    """
    if '/ShowUserReviews' in review_link:
        return re.findall("-r[0-9]{9}", review_link)[0][2:]
    else:
        return review_link


def extract_user_helpful_vote(vote_text):
    """
    Extract the number of helpful vote on user page

    :param vote_text: str
    :return: number of helpful vote: int

    >>> extract_user_helpful_vote('1 "Hilfreich"-Wertung')
    1
    """
    return int(vote_text[0])


def extract_user_review_helpful_vote(helpful_vote):
    """
    Extract the number of helpful vote on user review page

    :param helpful_vote: str
    :return: number: int

    >>> extract_user_review_helpful_vote('1 \xa0')
    1
    """
    return int(helpful_vote[0])


def extract_hotel_helpful_vote(review_helpful):
    """
    Extract the number of helpful vote on hotel page
    If the string contains only one number, it is the number of reviews,
    if it contains two numbers, the second number is the number of helpful reviews.

    :param review_helpful: str
    :return: helpful vote: int

    >>> extract_hotel_helpful_vote('45')
    0

    >>> extract_hotel_helpful_vote('15 3')
    3
    """
    if ' ' in review_helpful:
        return int(re.findall(' [0-9]+', review_helpful)[0][1:])
    else:
        return int(0)


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
    return re.findall("-d[0-9]+-", review_link)[0][2:-1]


class HotelItem(scrapy.Item):
    hotel_id = scrapy.Field(input_processor=MapCompose(remove_tags, extract_hotel_id),
                            output_processor=TakeFirst())
    hotel_name = scrapy.Field(input_processor=MapCompose(remove_tags, remove_unnecessary_whitespace),
                              output_processor=TakeFirst())
    hotel_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_score),
                               output_processor=TakeFirst())


class HotelReviewItem(scrapy.Item):
    review_id = scrapy.Field(input_processor=MapCompose(remove_tags),
                             output_processor=TakeFirst())
    username_id = scrapy.Field(input_processor=MapCompose(remove_tags, extract_username_id),
                               output_processor=TakeFirst())
    review_helpful_vote = scrapy.Field(input_processor=MapCompose(remove_tags),
                                       output_processor=Join())
    review_date = scrapy.Field(input_processor=MapCompose(remove_tags, extract_review_date),
                               output_processor=TakeFirst())
    date_of_stay = scrapy.Field(input_processor=MapCompose(remove_tags, extract_date_of_stay_review),
                                output_processor=TakeFirst())
    review_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_score),
                                output_processor=TakeFirst())
    review_title = scrapy.Field(input_processor=MapCompose(remove_tags),
                                output_processor=TakeFirst())
    review_text = scrapy.Field(input_processor=MapCompose(remove_tags),
                               output_processor=Join())


class UserReviewPage(scrapy.Item):
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
    review_date = scrapy.Field(input_processor=MapCompose(remove_tags),
                               output_processor=TakeFirst())
    date_of_stay = scrapy.Field(input_processor=MapCompose(remove_tags, extract_date_of_stay_array),
                                output_processor=Join())
    review_score = scrapy.Field(input_processor=MapCompose(remove_tags, extract_score),
                                output_processor=TakeFirst())
    review_title = scrapy.Field(input_processor=MapCompose(remove_tags),
                                output_processor=TakeFirst())
    review_text = scrapy.Field(input_processor=MapCompose(remove_tags),
                               output_processor=TakeFirst())
