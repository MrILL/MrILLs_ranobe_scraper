from flask import Flask
from flask import request
from flask.json import jsonify
import cloudscraper

app = Flask(__name__)
scraper = cloudscraper.create_scraper()

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url', default='')
    if not url:
        return 'Bad Request', 400

    page = scraper.get(url).text
    if not page:
        return "Can't Scrape Site", 418 

    return {
        "page": page,
    }, 200
