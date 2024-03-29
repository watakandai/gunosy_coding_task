from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup


def html_to_text_img(url):
    """
    reads html and parse into text and img data

    Parameter
    ------------
    url: str
        a url

    Returns
    -------------
    title: str
        title of an article
    text: str
        article contents
    img_url: str
        url of an image

    """
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

    title = soup.find("h1").get_text()
    text = ''
    ps = soup.find("div", {"class": "article gtm-click"}).find_all('p')
    for p in ps:
        text += ''.join(p.get_text())
    imgs = soup.select("div.article__image img")
    img_url = imgs[0]['data-src']

    return title, text, img_url
