import math
import dill


class NaiveBayes():
    """
    A classifier that predicts a category from a list of words
    P(C) = category_1 / all categories
    P(D|C) = { word_1 / all words in a category }

    Parameters
    ------------------
    T: a list
        a list of teacher data
    filename: str
        a name of a file to store parameters
    """
    def __init__(self, T, filename='naive_bayes_params.pkl'):
        self.T = T
        self.filename = filename
        self.words = set()
        self.P_C = Probability(T)
        self.P_DC = ConditionalProbability(T)

    def fit(self, X, T):
        # count word frequency for each word in each category
        for t, xs in zip(T, X):
            for x in xs:
                self.words.add(x)
                self.P_C.increment(t)
                self.P_DC.increment(x, t)

        # normalize values to get percentage
        self.P_C.normalize()
        self.P_DC.normalize(len(self.words))

        # save parameters
        with open(self.filename, 'wb') as f:
            f.write(dill.dumps([self.P_C, self.P_DC]))

        return [self.P_C, self.P_DC]

    def load_params(self):
        # load parameters from pkl file
        with open(self.filename, 'rb') as f:
            self.P_C, self.P_DC = dill.loads(f.read())

    def predict(self, xs):
        # calculate score of a given data x
        scores = []
        for t in self.T:
            score = math.log(self.P_C.get(t))
            for x in xs:
                p_dc = self.P_DC.get(x, t)
                score += math.log(p_dc)
            scores.append(score)

        # choose the highest score category as a predicted category
        indx = scores.index(max(scores))
        category = self.T[indx]

        return category

    def score(self, X, T, verbose=False):
        # check if predicted class is correct
        predicted = []
        accuracy = 0
        for t, xs in zip(T, X):
            pred = self.predict(xs)
            if pred == t:
                accuracy += 1
            predicted.append(pred)
            if verbose is True:
                print('(Pred,Ans): (%s, %s)' % (pred, t))

        return accuracy / len(T)


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
                self.dict[key] = self.dict[key] / sum_of_values

    def normalize_with_smoothing(self, X_count):
        self.X_count = X_count
        sum_of_values = sum(self.dict.values())
        if sum_of_values is not 0:
            for key in self.dict:
                self.dict[key] = (self.dict[key] + 1) / (sum_of_values + X_count)

    def get(self, key):
        if self.dict.get(key) is None:
            return 1 / self.X_count
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
            return 1 / len(self.T)
        else:
            return self.dict[t].get(x)
