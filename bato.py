import scrapy
import urlparse
from tmp.settings import USERNAME
from tmp.settings import PASSWORD
from scrapy.http import FormRequest


class Bato(scrapy.Spider):
    name = 'bato'
    start_urls = ['https://bato.to/']
    download_delay = 1

    def parse(self, response):
        if 'Sign In' in response.body:
            self.log("Logging in")
            yield FormRequest.from_response(response,
                                            formxpath="//*[@id='login'\
                                            ]/div[2]",
                                            formdata={
                                                'ips_username': USERNAME,
                                                'ips_password': PASSWORD},
                                            callback=self.after_login)
        else:
            self.after_login(response)

    def after_login(self, response):
        if not "Welcome, " + USERNAME in response.body:
            self.log("Login failed")
            return
        elif "Sign Out":
            self.log("Login successful")
            yield scrapy.Request('http://bato.to/myfollows',
                                 callback=self.parse_follows)

    def parse_follows(self, response):
        if not "Welcome, " + USERNAME in response.body:
            self.log("Login failed")
            return
        elif "Sign Out":
            self.log("Login successful {0}".format(response.url))
            anchors = response.selector.xpath(
                ".//div[@id='content']/div[3]/descendant::div[position()\
                >= 3]/a")
            for anchor in anchors:
                link = anchor.xpath('./@href').extract()
                name = anchor.xpath('./text()').extract()
                link = urlparse.urljoin('https://bato.to/', link[0])
                yield {'name': name[0], 'link': link}
