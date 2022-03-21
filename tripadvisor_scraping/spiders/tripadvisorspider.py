import scrapy
from tripadvisor_scraping.items import HotelReviewItem
from scrapy.loader import ItemLoader


class TripadvisorSpider(scrapy.Spider):
    name = 'tripadvisor'
    # start_urls = ['https://www.tripadvisor.ch/Hotel_Review-g188064-d206048-Reviews-Hotel_des_Balances-Lucerne.html']
    start_urls = ['https://www.tripadvisor.ch/Hotel_Review-g5237954-d7378599-Reviews-Greuterhof-Islikon_Canton_of_Thurgau.html']

    def parse(self, response):
        for hotel_review in response.css('div[data-test-target=reviews-tab]').css('div.cWwQK.MC.R2.Gi.z.Z.BB.dXjiy'):
            # Need a better solutions then try and except. Needs it, because helpful votes isn't always given
            # Why does 4 Reviews missing
            hr = ItemLoader(item=HotelReviewItem(), selector=hotel_review)

            hr.add_css('username', 'a.ui_header_link::text')
            hr.add_css('review_helpful_vote', 'span.ckXjS::text')
            hr.add_css('review_date', 'div.bcaHz span::text')
            hr.add_css('review_score', 'span.ui_bubble_rating::attr(class)')
            hr.add_css('review_id', 'div.cqoFv._T::attr(data-reviewid)')
            hr.add_css('review_title', 'a.fCitC span::text')
            hr.add_css('review_text', 'q.XllAv.H4._a span::text')

            yield hr.load_item()

                    # 'review_helpful_vote': int(reviews.css('span.ckXjS::text').extract()[1])

                    # 'username': reviews.css('a.ui_header_link::text').get(),
                    # 'review_helpful_vote': 0,
                    # 'review_date': self.extractReviewDate(reviews.css('div.bcaHz').css('span::text').get()), # Extract the date out of the string
                    # 'review_score': reviews.css('span.ui_bubble_rating::attr(class)').get().replace('ui_bubble_rating ', '')[-2], # Score is a class like bubble_50 for 5, just return the score
                    # 'review_id': reviews.css('div.cqoFv._T::attr(data-reviewid)').get(),
                    # 'review_title': reviews.css('a.fCitC').css('span::text').get(),
                    # 'review_text': reviews.css('q.XllAv.H4._a').css('span::text').get(),

        # Go to next review page
        next_page = response.css('a.ui_button.nav.next.primary::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
