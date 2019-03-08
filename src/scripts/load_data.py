"""
This script loads train and test data
"""
import os
from time import sleep
import dill
import random
import sqlite3
from janome.tokenizer import Tokenizer


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
        self.curs.execute("SELECT %s FROM %s" % (s, self.table_name))
        return self.curs.fetchall()

    def select_all(self):
        """selects all the columns from the table"""
        return self.select('*')


def load_data(db_name, table_name, word_class=["名詞", "動詞"], filename='train_data.pkl', use_pkl=True):
    """
    loads data and parse sentence into words
    data:  [(cat1, sentenc1)]
    storage:  [(cat1,word1), ..., (catn,wordn)]
    """
    # Load parsed data if specified, else parse raw data
    if use_pkl is True:
        # load parameters from pkl file
        with open(filename, 'rb') as f:
            categories, Words = dill.loads(f.read())
    else:
        # connect to database
        db_manager = DBManager(db_name=db_name, table_name=table_name)
        # load data
        raw_data = db_manager.select_all()

        # Morphological Analyzer
        ma = MorphologicalAnalyzer(word_class=word_class)
        # divide into words using morphological analysis
        categories = []
        Words = []
        for data in raw_data:
                category = data[1]
                words = ma.split(data[2])
                categories.append(category)
                Words.append(words)

        # save parameters
        with open(filename, 'wb') as f:
            f.write(dill.dumps([categories, Words]))

    return categories, Words


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
