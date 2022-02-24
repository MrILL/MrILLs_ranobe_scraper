import cloudscraper

site = "https://ranobes.com/chapters/solo-leveling-org/23557-tom-1-glava-1-ohotnik-ranga-e.html"

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
# Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
print(scraper.get(site).text)  # => "<!DOCTYPE html><html><head>..."