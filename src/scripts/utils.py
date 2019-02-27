from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import logging


def html_to_text_img(url):
    if url is '' or url is None:
        return None
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        return None
    except URLError as e:
        print(e)
        return None

    try:
        soup = BeautifulSoup(html.read(), "html.parser")
    except AttributeError as e:
        print(e)
        return None

    text = soup.find("h1").get_text()
    imgs = soup.select("div.article__image img")
    first_img_url = imgs[0]['data-src']

    return text, first_img_url
