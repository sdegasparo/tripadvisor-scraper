# Tripadvisor Scraper with Scrapy, ScrapingBee / Splash

Install the requirements `pip install -r requirements.txt`

## Scrape
* Run Scrapy: `scrapy crawl tripadvisor`
* Run Scrapy with output to json: `scrapy crawl tripadvisor -o tripadvisor.json`

## Scrapy Shell
* `scrapy shell URL`
* With Splash `scrapy shell` and then `fetch('http://localhost:8050/render.html?url=URL')`

## Run Doctest
`python -m doctest items.py -v`