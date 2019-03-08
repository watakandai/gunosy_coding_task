import dill
from django.shortcuts import render
from django.http import HttpResponse
from scripts.html_to_text_img import html_to_text_img
from scripts.utils import MorphologicalAnalyzer as MA
import sys
from scripts import classifiers
sys.modules['classifiers'] = classifiers

categories = {
    'https://gunosy.com/categories/1': 'ENTERTAINMENT',
    'https://gunosy.com/categories/2': 'SPORT',
    'https://gunosy.com/categories/3': 'GAGS',
    'https://gunosy.com/categories/4': 'DOMESTIC',
    'https://gunosy.com/categories/5': 'INTERNATIONAL',
    'https://gunosy.com/categories/6': 'COLUMN',
    'https://gunosy.com/categories/7': 'IT',
    'https://gunosy.com/categories/8': 'GOURMET',
}
category_lists = list(categories.values())
nb = classifiers.NaiveBayes(T=category_lists)
nb.load_params()
ma = MA(word_class=["名詞", "動詞"])


def home(request):
    global nb
    url = request.GET.get('url')
    print(url)
    if url is not None:
        article_title, article_text, img_url = html_to_text_img(url)
        img_url = 'https:' + img_url
        words = ma.split(article_text)
        category, _ = nb.predict(words)
    else:
        article_title = None
        article_text = None
        img_url = None
        category = None

    return render(request, 'form.html', {
        'article_title': article_title,
        'article_text': article_text,
        'category': category,
        'img_url': img_url})
