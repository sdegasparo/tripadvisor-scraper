import scrapy
from tripadvisor_scraping.items import HotelItem, HotelReviewItem, UserReviewItem
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest


class TripadvisorSpider(scrapy.Spider):
    name = 'tripadvisor'
    # start_urls = ['https://www.tripadvisor.ch/Hotel_Review-g910519-d1513327-Reviews-Hotel_Murten-Murten_Canton_of_Fribourg.html']
    start_urls = ['https://www.tripadvisor.ch/Hotels-g910519-Murten_Canton_of_Fribourg-Hotels.html']

    def parse(self, response):
        for hotel in response.css('div.prw_rup.prw_meta_hsx_responsive_listing.ui_section.listItem'):
            h = ItemLoader(item=HotelItem(), selector=hotel)
            h.add_css('hotel_id', 'div.meta_listing.ui_columns::attr(data-listingkey)')
            h.add_css('hotel_name', 'div.listing_title a.property_title.prominent::text')
            h.add_css('hotel_score', 'a.ui_bubble_rating::attr(class)')
            yield h.load_item()

            # Go through all hotels on this page
            hotel_link = hotel.css('div.listing_title a.property_title.prominent::attr(href)').get()
            if hotel_link is not None:
                yield response.follow(hotel_link, callback=self.parse_hotel_review)

            # Go to next page
            next_hotel_page = response.css('a.nav.next.ui_button.primary::attr(href)').get()
            if next_hotel_page is not None:
                yield response.follow(next_hotel_page, callback=self.parse)

    def parse_hotel_review(self, response):
        for hotel_review in response.css('div[data-test-target=reviews-tab] div.cWwQK.MC.R2.Gi.z.Z.BB.dXjiy'):
            hr = ItemLoader(item=HotelReviewItem(), selector=hotel_review)
            # TODO also add hotel_id and hotel_name to hotel_review loader, but the information isn't on this page
            hr.add_css('review_id', 'div.cqoFv._T::attr(data-reviewid)')
            hr.add_css('username_id', 'div.bcaHz a.ui_header_link.bPvDb::attr(href)')
            # hr.add_css('review_helpful_vote', 'span.eUTJT:last-child span.ckXjS::text')
            hr.add_css('review_helpful_vote', 'span.eUTJT span.ckXjS::text')
            hr.add_css('review_date', 'div.bcaHz span::text')
            hr.add_css('date_of_stay', 'span.euPKI._R.Me.S4.H3::text')
            hr.add_css('review_score', 'span.ui_bubble_rating::attr(class)')
            hr.add_css('review_title', 'a.fCitC span::text')
            hr.add_css('review_text', 'q.XllAv.H4._a span::text')
            yield hr.load_item()

            # Go to user page
            user_link = hotel_review.css('div.bcaHz a.ui_header_link.bPvDb::attr(href)').get()
            url = 'https://www.tripadvisor.ch' + user_link
            yield SplashRequest(url=url, callback=self.parse_user_page)

        # Go to next review page
        next_hotel_review_page = response.css('a.ui_button.nav.next.primary::attr(href)').get()
        if next_hotel_review_page is not None:
            yield response.follow(next_hotel_review_page, callback=self.parse_hotel_review)

    def parse_user_page(self, response):
        for user_review in response.css('div.eSYSx.ui_card.section'):
            # Check if it's a hotel review
            if 'hotels' in user_review.css('span.ui_icon.fuEgg::attr(class)').get():
                review_page = user_review.css('div.bCnPW.Pd a::attr(href)').get()
                if review_page is not None:
                    yield response.follow(review_page, callback=self.parse_user_review)

    def parse_user_review(self, response):
        user_review = response.css('div.review-container')
        ur = ItemLoader(item=UserReviewItem(), selector=user_review)
        ur.add_css('username_id', 'div.member_info div.info_text div::text')
        ur.add_css('review_id', 'div.altHeadInline a::attr(href)')
        ur.add_css('review_helpful_vote', 'div.helpful span.helpful_text span.numHelp::text')
        ur.add_css('review_date', 'span.ratingDate::attr(title)')
        ur.add_css('date_of_stay', 'div.prw_rup.prw_reviews_stay_date_hsx::text')
        ur.add_css('review_score', 'span.ui_bubble_rating::attr(class)')
        # ur.add_css('hotel_score', 'div.ui_poi_review_rating span.ui_bubble_rating::attr(class)') Gibt es nicht auf dieser Seite
        ur.add_css('review_title', 'h1.title::text')
        ur.add_css('review_text', 'div.prw_rup.prw_reviews_resp_sur_review_text span.fullText::text')

    # def parse_user_review_alt(self, response):
    #     for user_review in response.css('div.eSYSx.ui_card.section'):
    #         # TODO press Load More Button
    #
    #         # Check if it's a hotel review
    #         if 'hotels' in user_review.css('span.ui_icon.fuEgg::attr(class)').get():
    #             ur = ItemLoader(item=UserReviewItem(), selector=user_review)
    #             ur.add_css('username_id', 'a.bugwz.I.ui_social_avatar::attr(href)')
    #             ur.add_css('review_id', 'div.bCnPW.Pd a::attr(href)')
    #             # ur.add_css('review_id', 'span.wlOhd a.ui_link::attr(href)')
    #             ur.add_css('review_helpful_vote', 'span.ekLsQ.S2.H2.Ch.bzShB::text')
    #             ur.add_css('review_date', 'span.wlOhd a.ui_link::text')
    #             ur.add_css('date_of_stay', 'div.cXdic.S4.H3.Ci span::text') # TODO Check if it's right
    #             ur.add_css('review_score', 'div.cncQp.eCoog span.ui_bubble_rating::attr(class)')
    #             ur.add_css('hotel_score', 'div.ui_poi_review_rating span.ui_bubble_rating::attr(class)')
    #             ur.add_css('review_title', 'div.fpXkH.b._a.eCoog::text')
    #             ur.add_css('review_text', 'q.egSFv::text') # TODO Get whole text, if isn't possible maybe go to every review page
