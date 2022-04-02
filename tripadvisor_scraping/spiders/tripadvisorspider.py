import scrapy
from tripadvisor_scraping.items import HotelItem, HotelIdReviewIdItem, UserReviewItem
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy_scrapingbee import ScrapingBeeSpider, ScrapingBeeRequest


class TripadvisorSpider(ScrapingBeeSpider):
    # class TripadvisorSpider(scrapy.Spider):
    name = 'tripadvisor'

    # Test URL Murten
    start_urls = ['https://www.tripadvisor.ch/Hotels-g910519-Murten_Canton_of_Fribourg-Hotels.html']

    # Prod URL Switzerland
    # start_urls = ['https://www.tripadvisor.ch/Hotels-g910519-Murten_Canton_of_Fribourg-Hotels.html']

    def parse(self, response):
        for hotel in response.css('div.prw_rup.prw_meta_hsx_responsive_listing.ui_section.listItem'):
            h = ItemLoader(item=HotelItem(), selector=hotel)
            h.add_css('hotel_id', 'div.listing_title a::attr(href)')
            h.add_css('hotel_name', 'div.listing_title a.property_title.prominent::text')
            h.add_css('hotel_score', 'a.ui_bubble_rating::attr(class)')
            yield h.load_item()

            # Go through all hotels on this page
            hotel_link = hotel.css('div.listing_title a.property_title.prominent::attr(href)').get()
            if hotel_link is not None:
                yield response.follow(hotel_link, callback=self.parse_hotel_page)

            # Go to next page
            next_hotel_page = response.css('a.nav.next.ui_button.primary::attr(href)').get()
            if next_hotel_page is not None:
                yield response.follow(next_hotel_page, callback=self.parse)

    def parse_hotel_page(self, response):
        for hotel_review in response.css('div[data-test-target=reviews-tab] div.cWwQK.MC.R2.Gi.z.Z.BB.dXjiy'):
            # Go to user page
            user_link = hotel_review.css('div.bcaHz a.ui_header_link.bPvDb::attr(href)').get()
            url = 'https://www.tripadvisor.ch' + str(user_link)
            yield ScrapingBeeRequest(url=url, callback=self.parse_user_page)
            # yield SplashRequest(url=url, callback=self.parse_user_page)

        # Go to next review page
        next_hotel_review_page = response.css('a.ui_button.nav.next.primary::attr(href)').get()
        if next_hotel_review_page is not None:
            yield response.follow(next_hotel_review_page, callback=self.parse_hotel_page)

    def parse_user_page(self, response):
        for user_review in response.css('div.eSYSx.ui_card.section'):
            # Check if it's a hotel review
            ui_icon_class = user_review.css('span.ui_icon.fuEgg::attr(class)').get()
            if ui_icon_class is not None:
                if 'hotels' in ui_icon_class:

                    hr = ItemLoader(item=HotelIdReviewIdItem(), selector=user_review)
                    hr.add_css('hotel_id', 'div.bCnPW.Pd a::attr(href)')
                    hr.add_css('review_id', 'div.bCnPW.Pd a::attr(href)')
                    yield hr.load_item()

                    review_page = user_review.css('div.bCnPW.Pd a::attr(href)').get()
                    url = 'https://www.tripadvisor.ch' + str(review_page)
                    if review_page is not None:
                        # yield SplashRequest(url=url, callback=self.parse_user_review)
                        yield ScrapingBeeRequest(url=url, callback=self.parse_user_review)

    def parse_user_review(self, response):
        user_review = response.css('div.review-container')
        ur = ItemLoader(item=UserReviewItem(), selector=user_review)
        ur.add_css('username_id', 'div.member_info div.info_text div::text')
        ur.add_css('review_id', 'div.reviewSelector::attr(data-reviewid)')
        ur.add_css('review_helpful_vote', 'div.helpful span.helpful_text span.numHelp::text')
        ur.add_css('review_date', 'span.ratingDate::attr(title)')
        ur.add_css('date_of_stay', 'div.prw_rup.prw_reviews_stay_date_hsx::text')
        ur.add_css('review_score', 'span.ui_bubble_rating::attr(class)')
        ur.add_css('review_title', 'h1.title::text')
        ur.add_css('review_text', 'div.prw_rup.prw_reviews_resp_sur_review_text span.fullText::text')
        yield ur.load_item()
