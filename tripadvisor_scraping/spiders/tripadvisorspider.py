import scrapy
from tripadvisor_scraping.items import HotelItem, HotelIdReviewIdItem, UserItem, UserReviewItem
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy_scrapingbee import ScrapingBeeSpider, ScrapingBeeRequest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

import time


class TripadvisorSpider(ScrapingBeeSpider):
    # class TripadvisorSpider(scrapy.Spider):
    name = 'tripadvisor'

    # Test URL Murten
    start_urls = ['https://www.tripadvisor.ch/Hotels-g910519-Murten_Canton_of_Fribourg-Hotels.html']

    # Prod URL Switzerland
    # start_urls = ['https://www.tripadvisor.ch/Hotels-g188045-Switzerland-Hotels.html']

    @staticmethod
    def load_more_reviews(url):
        """
        Use Selenium to click on load more button.
        Scroll to the bottom of the page to load more reviews, until all reviews are loaded

        :param url: str
        :return: user_reviews: scrapy response
        """
        options = Options
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element(by=By.CSS_SELECTOR, value='div#content div.cGWLI.Mh.f.j button').click()

        previous_height = driver.execute_script('return document.body.scrollHeight')
        # Scroll to the bottom of the page to load more reviews, until all reviews are loaded
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == previous_height:
                break
            else:
                previous_height = new_height

        # Transform the page HTML into a Scrapy response
        response = scrapy.Selector(text=driver.page_source.encode('utf-8'))
        user_reviews = response.css('div.eSYSx.ui_card.section')
        driver.close()

        return user_reviews

    def parse(self, response):
        for hotel in response.css('div.prw_rup.prw_meta_hsx_responsive_listing.ui_section.listItem'):
            # Go through all hotels on this page
            hotel_link = hotel.css('div.listing_title a.property_title.prominent::attr(href)').get()
            if hotel_link is not None:
                yield response.follow(hotel_link, callback=self.parse_hotel_page)

        # Go to next hotel page
        next_hotel_page = response.css('a.nav.next.ui_button.primary::attr(href)').get()
        if next_hotel_page is not None:
            yield response.follow(next_hotel_page, callback=self.parse)

    def parse_hotel_page(self, response):
        h = ItemLoader(item=HotelItem(), response=response)
        h.add_css('h_hotel_id', 'div.badtN a::attr(href)')
        h.add_css('h_hotel_name', 'h1.fkWsC.b.d.Pn::text')
        h.add_css('h_hotel_score', 'div.bSlOX.P span.bvcwU.P::text')
        h.add_css('h_hotel_description', 'div.duhwe._T.bOlcm.bWqJN.Ci.dMbup div.pIRBV._T::text')
        yield h.load_item()

        for hotel_review in response.css('div[data-test-target=reviews-tab] div.cWwQK.MC.R2.Gi.z.Z.BB.dXjiy'):
            # Go to user page
            user_link = hotel_review.css('div.bcaHz a.ui_header_link.bPvDb::attr(href)').get()
            url = 'https://www.tripadvisor.ch' + str(user_link)
            yield ScrapingBeeRequest(url=url, callback=self.parse_user_page, cb_kwargs=dict(url=url))
            # yield SplashRequest(url=url, callback=self.parse_user_page)

        # Go to next review page
        next_hotel_review_page = response.css('a.ui_button.nav.next.primary::attr(href)').get()
        if next_hotel_review_page is not None:
            yield response.follow(next_hotel_review_page, callback=self.parse_hotel_page)

    def parse_user_page(self, response, url):
        username_id = response.css('div.dGTGf.f.K.MD span.mDiUf._R::text').get()
        user_info = response.css('div.duHGF.MD.ui_card.section')
        u = ItemLoader(item=UserItem(), selector=user_info)
        u.add_value('u_username_id', username_id)
        u.add_css('u_user_location', 'span.fIKCp._R.S4.H3.ShLyt.default::text')
        u.add_css('u_user_register_date', 'span.dspcc._R.H3::text')
        yield u.load_item()

        # Check if it has a load more button on the user page
        load_more_button = response.css(
            'div.cGWLI.Mh.f.j button.fGwNR._G.B-.z._S.c.Wc.ddFHE.eMHQC.brHeh.bXBfK span.cdYjE.Vm::text').get()
        if load_more_button is not None:
            # Use Selenium to click on the load more button and scroll to the bottom
            user_reviews = self.load_more_reviews(url)
        else:
            user_reviews = response.css('div.eSYSx.ui_card.section')

        for user_review in user_reviews:
            # Check if it's a hotel review
            ui_icon_class = user_review.css('span.ui_icon.fuEgg::attr(class)').get()
            if ui_icon_class is not None:
                if 'hotels' in ui_icon_class:

                    hr = ItemLoader(item=HotelIdReviewIdItem(), selector=user_review)
                    hr.add_css('hr_hotel_id', 'div.bCnPW.Pd a::attr(href)')
                    hr.add_css('hr_review_id', 'div.bCnPW.Pd a::attr(href)')
                    yield hr.load_item()

                    review_page = user_review.css('div.bCnPW.Pd a::attr(href)').get()
                    url = 'https://www.tripadvisor.ch' + str(review_page)
                    if review_page is not None:
                        # yield SplashRequest(url=url, callback=self.parse_user_review)
                        yield ScrapingBeeRequest(url=url, callback=self.parse_user_review)

    def parse_user_review(self, response):
        user_review = response.css('div.review-container')
        helpful_vote = user_review.css('div.helpful span.helpful_text span.numHelp::text').get()
        ur = ItemLoader(item=UserReviewItem(), selector=user_review)
        ur.add_css('ur_username_id', 'div.member_info div.info_text div::text')
        ur.add_css('ur_review_id', 'div.reviewSelector::attr(data-reviewid)')
        ur.add_css('ur_review_date', 'span.ratingDate::attr(title)')
        ur.add_css('ur_date_of_stay', 'div.prw_rup.prw_reviews_stay_date_hsx::text')
        ur.add_css('ur_review_score', 'span.ui_bubble_rating::attr(class)')
        ur.add_css('ur_review_title', 'h1.title::text')
        ur.add_css('ur_review_text', 'div.prw_rup.prw_reviews_resp_sur_review_text span.fullText::text')

        if helpful_vote is not None:
            ur.add_value('ur_review_helpful_vote', int(helpful_vote[0]))
        else:
            ur.add_value('ur_review_helpful_vote', int(0))

        yield ur.load_item()
