import scrapy
from tripadvisor_scraping.items import HotelItem, HotelIdReviewIdItem, UserItem, UserReviewItem
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy_scrapingbee import ScrapingBeeSpider, ScrapingBeeRequest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import csv

import time
import logging


class TripadvisorSpider(ScrapingBeeSpider):
    # class TripadvisorSpider(scrapy.Spider):
    name = 'tripadvisor'

    # Start URL for scraping
    # start_urls = ['https://www.tripadvisor.ch/']

    # Extract all Hotel URL Switzerland
    start_urls = ['https://www.tripadvisor.ch/Hotels-g188045-Switzerland-Hotels.html']

    @staticmethod
    def get_all_hotel_links(response):
        # Use Selenium to click on next page button on the hotel site.
        # Because the next site is loaded dynamic.
        options = Options()
        options.headless = False
        driver = webdriver.Firefox(options=options)
        driver.get(response.request.url)

        last_page = False
        hotel_links = []

        # Click Load More Button
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            driver.find_element(by=By.CSS_SELECTOR,
                                value='div.Gi.Z.B1.BB.P5.Mj.f.j button.rmyCe._G.B-.z._S.c.Wc.wSSLS.pexOo.sOtnj').click()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except:
            pass

        while not last_page:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Check if the page is loaded
            try:
                loading = EC.invisibility_of_element_located((By.ID, 'taplc_hotels_loading_box_0'))
                WebDriverWait(driver, 30).until(loading)
            except TimeoutException:
                print('No Button')

            # Transform the page HTML into a Scrapy response
            response_hotel = scrapy.Selector(text=driver.page_source.encode('utf-8'))
            for hotel in response_hotel.css('div.prw_rup.prw_meta_hsx_responsive_listing.ui_section.listItem'):
                hotel_link = hotel.css('div.listing_title a.property_title.prominent::attr(href)').get()
                hotel_links.append(hotel_link)

            # Go to next hotel list page
            try:
                driver.find_element(by=By.CSS_SELECTOR,
                                    value='div.unified.ui_pagination.standard_pagination.ui_section.listFooter span.nav.next.ui_button.primary.disabled')
                print('Button disabled')
                last_page = True
            except NoSuchElementException:
                driver.find_element(by=By.CSS_SELECTOR,
                                    value='div.unified.ui_pagination.standard_pagination.ui_section.listFooter span.nav.next.ui_button.primary').click()

        with open('hotel_links.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(hotel_links)

    def parse(self, response):
        # Save all hotel links in a csv file, because Selenium use too much memory when running in parallel
        self.get_all_hotel_links(response)

        # Load csv file with all hotel links
        # with open('hotel_links.csv') as csvfile:
        #     hotel_links = list(csv.reader(csvfile, delimiter=','))
        #
        # for hotel_link in hotel_links:
        #     yield response.follow(str(hotel_link), callback=self.parse_hotel_page)

    def parse_hotel_page(self, response):
        # Get hotel information
        h = ItemLoader(item=HotelItem(), response=response)
        h.add_css('h_hotel_id', 'div.lDMPR._m div.woPbY a::attr(href)')
        h.add_css('h_hotel_name', 'h1.QdLfr.b.d.Pn::text')
        h.add_css('h_hotel_score', 'div.chGvF.P span.IHSLZ.P::text')
        h.add_css('h_hotel_description', 'div._T.FKffI.IGtbc.Ci.oYqEM.Ps.Z.BB div.fIrGe._T::text')
        yield h.load_item()

        for hotel_review in response.css('div[data-test-target=HR_CC_CARD]'):
            # Get hotel_id and review_id
            hr = ItemLoader(item=HotelIdReviewIdItem(), selector=hotel_review)
            hr.add_css('hr_hotel_id', 'div[data-test-target=review-title] a.Qwuub::attr(href)')
            hr.add_css('hr_review_id', 'div[data-test-target=review-title] a.Qwuub::attr(href)')
            yield hr.load_item()

            # Go to user page
            user_link = hotel_review.css('div.cRVSd a.ui_header_link.uyyBf::attr(href)').get()
            user_url = 'https://www.tripadvisor.ch' + str(user_link)
            yield ScrapingBeeRequest(url=user_url, callback=self.parse_user_page, cb_kwargs=dict(url=user_url))
            # yield SplashRequest(url=url, callback=self.parse_user_page)

            review_link = hotel_review.css('div[data-test-target=review-title] a.Qwuub::attr(href)').get()
            review_url = 'https://www.tripadvisor.ch' + str(review_link)
            username_id = hotel_review.css(
                'div[data-test-target=HR_CC_CARD] a.kjIqZ.I.ui_social_avatar.inline::attr(href)').get().replace('/Profile/', '')
            yield ScrapingBeeRequest(url=review_url, callback=self.parse_user_review,
                                     cb_kwargs=dict(username_id=username_id))

        # Go to next review page
        next_hotel_review_page = response.css('a.ui_button.nav.next.primary::attr(href)').get()
        if next_hotel_review_page is not None:
            yield response.follow(next_hotel_review_page, callback=self.parse_hotel_page)

    def parse_user_page(self, response, url):
        # Get user information
        username_id = response.css('span.ecLBS._R.shSnD span.Dsdjn._R::text').get()
        user_info = response.css('div.MD.ui_card.section')
        user_register_date = response.css('span.ECVao._R.H3::text').extract()[1]
        u = ItemLoader(item=UserItem(), selector=user_info)
        u.add_value('u_username_id', username_id)
        u.add_css('u_user_location', 'span.PacFI._R.S4.H3.LXUOn.default::text')
        u.add_value('u_user_register_date', user_register_date)
        yield u.load_item()

    def parse_user_review(self, response, username_id):
        # Get review information
        user_review = response.css('div.review-container')
        helpful_vote = user_review.css('div.helpful span.helpful_text span.numHelp::text').get()
        review_text = ' '.join(user_review.css('div.prw_rup.prw_reviews_resp_sur_review_text span.fullText::text').extract())
        ur = ItemLoader(item=UserReviewItem(), selector=user_review)
        ur.add_value('ur_username_id', username_id)
        ur.add_css('ur_review_id', 'div.reviewSelector::attr(data-reviewid)')
        ur.add_css('ur_review_date', 'span.ratingDate::attr(title)')
        ur.add_css('ur_date_of_stay', 'div.prw_rup.prw_reviews_stay_date_hsx::text')
        ur.add_css('ur_review_score', 'span.ui_bubble_rating::attr(class)')
        ur.add_css('ur_review_title', 'h1.title::text')
        ur.add_value('ur_review_text', review_text)

        if helpful_vote is not None:
            ur.add_value('ur_review_helpful_vote', int(helpful_vote[0]))
        else:
            ur.add_value('ur_review_helpful_vote', int(0))

        yield ur.load_item()
