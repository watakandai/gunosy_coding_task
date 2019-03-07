"""
This script collects data, train, and test classifiers.
"""
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


def collect_and_save_data(db_name='test.db', table_name='home_article'):
    """
    Collects title & category data from the Gunosy websites
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
                    page_title = category_page_object.find_all("div", {
                        "class": "list_title"})[i_article].a.get_text()
                except AttributeError as e:
                    print(e)
                    continue

                insert_sql = 'INSERT INTO {0} VALUES(?, ?, ?)'.format(table_name)
                data = (current_article, category_name, page_title)
                curs.execute(insert_sql, data)
                conn.commit()
                print("No:%s, Cat:%s, Title:%s)" %
                      (current_article, category_name, page_title))
                current_article = current_article + 1
                time.sleep(1)
    conn.close()


def test_classifier():
    """
    Trains classifiers with collected dataset that is saved in db
    After the traning, it saves its parameters as pickle data.
    """
    # Parameter
    table_name = 'home_article'
    train_db = 'train.db'
    test_db = 'test.db'
    # dict -> list
    category_lists = list(categories.values())
    print("Category Lists: ", *category_lists, sep=', ')

    # load train data
    train_data, train_T, train_X = load_data(train_db, table_name, filename='train_data.pkl', use_pkl=True)
    test_data, test_T, test_X = load_data(test_db, table_name, filename='test_data.pkl', use_pkl=True)
    # convert from ['a', 'b'] to ['a b'] for CountVectorizer
    train_X = [' '.join(X) for X in train_X]
    test_X = [' '.join(X) for X in test_X]
    # bag of words -> count each word frequency and turn into a numeric vector
    vectorizer = CountVectorizer(token_pattern=u'(?u)\\b\\w+\\b')
    train_X_features = vectorizer.fit_transform(train_X + test_X)

    # load classifiers
    clf = NaiveBayes(T=category_lists)
    rfc = RFC(n_estimators=100, n_jobs=-1)

    # train with traning data
    print('Start Training...')
    clf.train(train_data)
    rfc.fit(train_X_features[:len(train_T)], train_T)

    # test with test data
    result, accuracy = clf.test(test_data, verbose=False)
    print(accuracy)
    accuracy = rfc.score(train_X_features[len(train_T):], test_T)
    print(accuracy)

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options as follows')
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if args.collect:
        collect_and_save_data()
    if args.test:
        test_classifier()
