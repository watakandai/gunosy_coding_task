from django.shortcuts import render
from django.http import HttpResponse
from .forms import HomeForm
from scripts.utils import html_to_text_img
# from scripts.classifier import Classifier

# cf = Classifier('NaiveBayes')


def home(request):
    url = request.GET.get('url')
    article_text, img_url = html_to_text_img(url)
    # category = cf.classify(article_text)

    if article_text is None:
        category = "Please enter URL."
    else:
        category = article_text
    if img_url is not None:
        img_url = 'https:' + img_url

    return render(request, 'form.html', {
        'category': category,
        'img_url': img_url})
