"""
This script collects data, train, and test classifiers.
"""
import time
import sqlite3
import argparse
from enum import Enum
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from janome.tokenizer import Tokenizer
from classifiers import DocumentClassifier
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


def collect_and_save_data():
    """
    Collects title & category data from the Gunosy websites
    """
    # connect to database
    conn = sqlite3.connect(DB_NAME)
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
        page_urls = ["%s?page=%s" % (category_url, i_page)\
                    for i_page in range(PAGE_START, PAGE_END + 1)]

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
                        "class": "list_title"})\
                        [i_article].a.get_text()
                except AttributeError as e:
                    print(e)
                    continue

                insert_sql = 'INSERT INTO {0} VALUES(?, ?, ?)'.format(TABLE_NAME)
                data = (current_article, category_name, page_title)
                curs.execute(insert_sql, data)
                conn.commit()
                print("No:%s, Cat:%s, Title:%s)" %
                      (current_article, category_name, page_title))
                current_article = current_article + 1
                time.sleep(1)
    conn.close()


def train_classifier(classifier_name='naive_bayes'):
    """
    Trains classifiers with collected dataset
    that is saved in db
    After the traning, it saves its parameters
    as pickle data.

    Parameters
    ----------------
    classifier_name : str
        Name of the classifier
        Choose 'all' if all classifiers to be trained
    """
    # load data
    DB_NAME = 'train.db'
    TABLE_NAME = 'home_article'
    # dict -> list
    category_lists = list(categories.values())
    print("Category Lists: ", *category_lists, sep=', ')
    # load train data
    train_data = load_data(DB_NAME, TABLE_NAME, use_pkl=True)
    # load classifier
    cf = DocumentClassifier(T=category_lists, classifier_name=classifier_name)
    # train with traning data
    print('Start Training...')
    cf.model.train(train_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options as follows')
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--train', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if args.collect:
        collect_and_save_data()
    if args.train:
        train_classifier()
    if args.test:
        test_classifiers()
