"""
This script collects data, train, and test classifiers.
"""
import dill
import time
import sqlite3
import argparse
import numpy as np
from enum import Enum
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier as RFC
from classifiers import NaiveBayes
from load_data import load_data
# https://note.nkmk.me/python-janome-tutorial/


# list of categories
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


def collect_and_save_data(db_name='articles.db', table_name='home_article'):
    """
    Collects title & category data from the Gunosy websites

    Parameters
    --------------
    db_name: str
        name of a db
    table_name: str
        name of a table
    """
    # connect to database
    conn = sqlite3.connect(db_name)
    curs = conn.cursor()

    # How many Pages per category
    PAGE_START = 1
    PAGE_END = 5
    # How many articles per page
    ARTICLE_START = 0
    ARTICLE_END = 20
    # count all the article
    current_article = 1

    for category_url, category_name in categories.items():
        # Try retrieving html from url
        try:
            _ = urlopen(category_url)
        except HTTPError as e:
            print(e)
            continue

        # List of URLs of each page
        page_urls = ["%s?page=%s" % (category_url, i_page) for i_page in range(PAGE_START, PAGE_END + 1)]

        # For each page, get articles
        for page_url in page_urls:
            # Try retrieving html from url
            try:
                category_page_html = urlopen(page_url)
            except HTTPError as e:
                print(e)
                continue

            # parse html through bs4
            try:
                category_page_object = BeautifulSoup(category_page_html.read(), "html.parser")
            except URLError as e:
                print(e)
                continue

            for i_article in range(ARTICLE_START, ARTICLE_END):
                try:
                    article_heading = category_page_object.find_all("div", {
                        "class": "list_title"})[i_article]
                    article_title = article_heading.a.get_text()
                    article_url = article_heading.a.get("href")
                except AttributeError as e:
                    print(e)
                    continue

                try:
                    category_page_html = urlopen(article_url)
                except HTTPError as e:
                    print(e)
                    continue

                try:
                    article_page_object = BeautifulSoup(category_page_html.read(), "html.parser")
                except URLError as e:
                    print(e)
                    continue

                article_ps = article_page_object.find("div", {
                    "class": "article gtm-click"}).find_all('p')
                article_text = ''
                for p in article_ps:
                    article_text += ''.join(p.get_text())

                insert_sql = 'INSERT INTO {0} VALUES(?, ?, ?, ?)'.format(table_name)
                data = (current_article, category_name, article_title, article_text)
                curs.execute(insert_sql, data)
                conn.commit()
                print("No:%s, Cat:%s, Title:%s, Text:%s)" %
                      (current_article, category_name, article_title, article_text))
                current_article = current_article + 1
                time.sleep(1)
    conn.close()


def test_classifier():
    """
    Trains classifiers with collected dataset that is saved in db
    and test with test data which is separated with train data
    """
    # Parameter
    table_name = 'home_article'
    db_name = 'articles.db'
    category_lists = list(categories.values())
    TRAIN_TO_TEST_RATIO = 0.7

    # load train data
    T, _, X = load_data(db_name, table_name, shuffled=True, filename='data.pkl', use_pkl=True, verbose=False)
    data_len = len(T)
    train_len = int(TRAIN_TO_TEST_RATIO * data_len)

    # Bag of Words -> Word Frequency
    X_concat = [' '.join(x) for x in X]  # convert from ['a', 'b'] to ['a b']
    vectorizer = CountVectorizer(token_pattern=u'(?u)\\b\\w+\\b')
    features = vectorizer.fit_transform(X_concat)

    # load classifiers
    nb = NaiveBayes(T=category_lists)
    rfc = RFC(n_estimators=100, n_jobs=-1)

    # train with traning data
    nb.fit(X[:train_len], T[:train_len])
    rfc.fit(features[:train_len], T[:train_len])

    # test with test data
    accuracy_nb = nb.score(X[train_len:], T[train_len:], verbose=False)
    accuracy_rfc = rfc.score(features[train_len:], T[train_len:])
    print('Accuracy: Naive Bayes ... %2.5f' % (accuracy_nb))
    print('Accuracy: Random Forest ... %2.5f' % (accuracy_rfc))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options as follows')
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if args.collect:
        collect_and_save_data()
    if args.test:
        test_classifier()
