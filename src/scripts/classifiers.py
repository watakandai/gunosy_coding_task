"""
How to improve the accuracy!
1. Tweek Naive Bayes classifier
2. Choose other classifier
3. Mix

1. Naive Bayes
 - Selection of a word class (Morphological Analaysis)
 - Adaboost
"""

import math
import pickle
from utils import Probability, ConditionalProbability


class NaiveBayes():
    def __init__(self, T, filename='naive_bayes_params.pkl'):
        self.T = T
        self.filename = filename
        self.words = set()
        self.P_C = Probability(T)
        self.P_DC = ConditionalProbability(T)

    def train(self, data):
        """
        P(C) = Cat1 / Cat_all
              : how many cat1 out of all data
        P(D|C) = { word1 / word_all_within_cat1 }
              : how often word1 appeared in all words
                that only appeared in cat1
        """

        # count word frequency for each word in each category
        for d in data:
            for x in d.X:
                self.words.add(x)
                self.P_C.increment(d.t)
                self.P_DC.increment(x, d.t)

        # normalize values to get percentage
        self.P_C.normalize()
        self.P_DC.normalize(len(self.words))

        # save parameters
        with open(self.filename, 'wb') as f:
            pickle.dump([self.P_C, self.P_DC], f)

    def classify(self, X):
        # calculate score of a given data x
        scores = []
        for t in self.T:
            score = math.log(self.P_C.get(t))
            for x in X:
                p_dc = self.P_DC.get(x, t)
                score += math.log(p_dc)
            scores.append(score)

        # choose the highest score category as a predicted category
        indx = scores.index(max(scores))
        category = self.T[indx]

        return category

    def test(self, data, verbose=False):
        # load parameters from pkl file
        with open(self.filename, 'rb') as f:
            self.P_C, self.P_DC = pickle.load(f)

        # check if predicted class is correct
        predicted = []
        accuracy = 0
        for d in data:
            pred = self.classify(d.X)
            if pred == d.t:
                accuracy += 1
            predicted.append(pred)
            if verbose is True:
                print('(Pred,Ans): (%s, %s)' % (pred, d.t))
        # calculate accuracy from accumulated scores
        accuracy = accuracy / len(data)

        return predicted, accuracy
