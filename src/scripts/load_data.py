"""
This script loads train and test data
"""
import os
import dill
import random
import sqlite3
from time import sleep
from utils import ProgressPrinter, MorphologicalAnalyzer
from utils import replace_any_number_in_str_with_0


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


def load_data(db_name, table_name, word_class=["名詞", "動詞"], shuffled=True, filename='data.pkl', use_pkl=True, verbose=False):
    """
    loads data and parse sentence into words
    data:  [(cat1, sentenc1)]
    storage:  [(cat1,word1), ..., (catn,wordn)]
    """
    # Load parsed data if specified, else parse raw data
    if use_pkl is True:
        # load parameters from pkl file
        with open(filename, 'rb') as f:
            categories, titles, texts = dill.loads(f.read())
    else:
        # connect to database
        db_manager = DBManager(db_name=db_name, table_name=table_name)
        # load data
        raw_data = db_manager.select_all()

        # Morphological Analyzer
        ma = MorphologicalAnalyzer(word_class=word_class)
        # divide into words using morphological analysis
        categories = []
        titles = []
        texts = []
        i = 1
        progress = ProgressPrinter(len(raw_data))
        for data in raw_data:
            category = data[1]
            title = ma.split(replace_any_number_in_str_with_0(data[2]))
            text = ma.split(replace_any_number_in_str_with_0(data[3]))
            categories.append(category)
            titles.append(title)
            texts.append(text)
            progress.print('Num:%i, Cat:%s, Title:%s' % (i, category, title))
            if verbose is True:
                print('Num:%i, Cat:%s, Title:%s' % (i, category, title))
                print('Texts: %s' % (text))

        # save parameters
        with open(filename, 'wb') as f:
            f.write(dill.dumps([categories, titles, texts]))

    if shuffled is True:
        D = list(zip(categories, titles, texts))
        random.shuffle(D)
        categories, titles, texts = zip(*D)

    return categories, titles, texts
