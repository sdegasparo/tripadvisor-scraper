# Tripadvisor Scraper with Scrapy, ScrapingBee / Splash

Install the requirements `pip install -r requirements.txt`

## Scrape
* Run Scrapy: `scrapy crawl tripadvisor`
* Run Scrapy with output to json: `scrapy crawl tripadvisor -o tripadvisor.json`

## Scrapy Shell
* `scrapy shell URL`
* With Splash `scrapy shell` and then `fetch('http://localhost:8050/render.html?url=URL')`

## Scrapingbee API-Key
Create a `.env` file with `SCRAPINGBEE_API_KEY = 'YOUR_API_KEY'` <br>
If you haven't a Scrapingbee API-Key you can use scrapy-splash

## Run Doctest
`python -m doctest items.py -v`