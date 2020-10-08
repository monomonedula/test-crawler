import string
from random import randint, choice

import scrapy
from scrapy import FormRequest
from scrapy.linkextractors import LinkExtractor


class LifeomicSpider(scrapy.spiders.CrawlSpider):
    name = "lifeomic"

    start_urls = [
        "https://lifeomic.com/",
    ]

    results_file = "crawler-data.csv"

    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        "Sec-Fetch-User": "?1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }

    rules = [
        scrapy.spiders.Rule(
            link_extractor=LinkExtractor(
                allow_domains="lifeomic.com",
                restrict_xpaths="//a",
            ),
            callback="parse",
            follow=True,
        ),
    ]

    sent_forms = set()

    def parse(self, response, **kwargs):
        for request in form_requests(response, self.parse):
            form_signature = (request.url, request.method)
            if form_signature not in self.sent_forms:
                self.sent_forms.add(form_signature)
                yield request
        self.save_resp(response)
        yield from self._parse(response, **kwargs)

    def save_resp(self, response):
        with open(self.results_file, "a") as f:
            f.write(
                "{}\n".format(
                    "\t".join(
                        (
                            response.request.url,
                            response.request.method,
                            str(len(response.body)),
                        )
                    )
                )
            )


def form_requests(response, callback):
    for i, form in enumerate(response.xpath("//form")):
        yield FormRequest.from_response(
            response,
            formnumber=i,
            formdata=random_inputs_for(inputs_of(form)),
            callback=callback,
            dont_filter=True,
        )


def random_inputs_for(input_names):
    return {name: random_string(randint(1, 100)) for name in input_names}


def inputs_of(form):
    names = []
    for inp in form.xpath("//input"):
        if not inp.xpath("@value").get():
            names.append(inp.xpath("@name").get())
    return names


def random_string(length):
    letters = string.ascii_lowercase
    return "".join(choice(letters) for i in range(length))
