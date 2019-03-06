import math
import sys
import sqlite3
from janome.tokenizer import Tokenizer
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

class DBManager():
    """
    connect to a database and manage the data

    Parameters
    ----------------
    db_name: str
        name of a database
    table_name: str
        name of a table 
    """
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.table_name = table_name
        conn = sqlite3.connect(db_name)
        self.curs = conn.cursor()

    def select(self, s):
        """
        select data whose key is "s" from the table

        Parameters
        ----------------
        s: str
            name of a key (column) 
        """
        self.curs.execute("SELECT %s FROM %s"%(s, self.table_name))
        return self.curs.fetchall()

    def select_all(self):
        """selects all the columns from the table"""
        return self.select('*')


class Data():
    """
    Parameters
    --------------
    t: 
        teacher data
    x: 
        raw data
    """
    def __init__(self, X, t):
        self.X = X
        self.t = t


class MorphologicalAnalyzer():
    """
    analyze a sentence and divides into list of words
    
    Parameters
    --------------
    word_class: list of str
        word class you want 
    """
    def __init__(self, word_class=["形容詞", "形容動詞", "感動詞", "副詞", "連体詞", "名詞", "動詞"]):
        self.word_class = word_class

    def split(self, sentence, word_class=None):
        if word_class is None:
            word_class = self.word_class

        t = Tokenizer()
        return [token.surface for token in t.tokenize(sentence)
                if token.part_of_speech.split(',')[0] in self.word_class]


class Probability():
    def __init__(self, keys=None):
        self.dict = {}
        self.keys = []

        if keys is not None:
            self.keys = keys
            self.initialize(keys)

    def initialize(self, keys):
        for key in keys:
            self.dict[key] = 0  

    def increment(self, key):
        if self.dict.get(key) is None:
            # if a key does not exist
            # add the key to keys and dict 
            self.keys.append(key)
            self.dict[key] = 0
        else:
            # if key exist, increment
            self.dict[key] += 1

    def normalize(self):
        sum_of_values = sum(self.dict.values())
        if sum_of_values is not 0:
            for key in self.dict:
                self.dict[key] = self.dict[key]/sum_of_values

    def normalize_with_smoothing(self, X_count):
        self.X_count = X_count
        sum_of_values = sum(self.dict.values())
        if sum_of_values is not 0:
            for key in self.dict:
                self.dict[key] = (self.dict[key]+1)/(sum_of_values+X_count)


    def get(self, key):
        if self.dict.get(key) is None:
            return 1/self.X_count
        else:
            return self.dict[key]


class ConditionalProbability():
    def __init__(self, T):
        self.dict = {}
        self.T = T 
        self.initialize(T)

    def initialize(self, T):
        for t in T:
            self.dict[t] = Probability()

    def increment(self, x, t):
        self.dict[t].increment(x)

    def normalize(self, X_count):
        self.X_count = X_count
        for t in self.T:
            self.dict[t].normalize_with_smoothing(X_count)

    def get(self, x, t):
        if self.dict.get(t) is None:
            return 1/len(self.T)
        else:
            return self.dict[t].get(x)
