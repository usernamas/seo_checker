from threading import Thread
from requests_html import HTMLSession

class Scraper:

    def __init__(self, url):
        self.url = url
        self.session = HTMLSession()
        #self.session.browser
        self.r = self.session.get(url)
        self.r.html.render(keep_page=True)

    def scrap(self):
        pass
