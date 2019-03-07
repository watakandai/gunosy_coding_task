"""
This script loads train and test data
"""
import os
from time import sleep
import pickle
import random
import sqlite3
from utils import MorphologicalAnalyzer as MA
from utils import DBManager, Data


def load_data(db_name, table_name, word_class=["名詞", "動詞"], filename='parsed_data.pkl', use_pkl=True):
    """
    loads data and parse sentence into words
    data:  [(cat1, sentenc1)]
    storage:  [(cat1,word1), ..., (catn,wordn)]
    """
    if use_pkl is True:
        # load parameters from pkl file
        with open(filename, 'rb') as f:
            parsed_data = pickle.load(f)
    else:
        # connect to database
        db_manager = DBManager(db_name=db_name, table_name=table_name)
        # load data
        unparsed_data = db_manager.select_all()

        # Morphological Analyzer
        ma = MA(word_class=word_class)
        # divide into words using morphological analysis
        parsed_data = []
        for data in unparsed_data:
                category = data[1]
                words = ma.split(data[2])
                parsed_data.append(Data(words, category))

        # save parameters
        with open(filename, 'wb') as f:
                pickle.dump(parsed_data, f)

    return parsed_data
