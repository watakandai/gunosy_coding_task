import re
from janome.tokenizer import Tokenizer


class MorphologicalAnalyzer():
    """
    analyze a sentence and divides into list of words

    Attributes
    --------------
    word_class: list of str
        word classes to extract
    """
    def __init__(self, word_class=["形容詞", "形容動詞", "感動詞", "副詞", "連体詞", "名詞", "動詞"]):
        self.word_class = word_class

    def split(self, sentence, word_class=None):
        """
        Parameters
        ------------------
        sentence: str
            sentence to be split
        """
        if word_class is None:
            word_class = self.word_class

        t = Tokenizer()
        return [token.surface for token in t.tokenize(sentence)
                if token.part_of_speech.split(',')[0] in self.word_class]


class ProgressPrinter():
    """
    it frequently prints a progress percentage
    and also prints out a str given as an argument

    Attributes
    ---------------
    iter_max: int
        max number of iterations
    interval: float
        determines frequency of print message
    curr_thres: float
        current threshold which will be incremented
    i: int
        current iteration
    """
    def __init__(self, iter_max, interval=0.1):
        self.iter_max = iter_max
        self.interval = interval
        self.curr_thres = interval
        self.i = 1

    def print(self, msg=None):
        ratio = float(self.i / self.iter_max)
        if ratio >= self.curr_thres:
            print('Progress: %0.2f' % (self.curr_thres))
            if msg is not None:
                print(msg)
            self.curr_thres += self.interval
        self.i += 1


def replace_any_number_in_str_with_0(text):
    """
    replace any number with 0 in a string

    Parameter
    --------------
    text: str
        a sentence
    """
    replaced_text = re.sub(r'\d+', '0', text)
    return replaced_text
