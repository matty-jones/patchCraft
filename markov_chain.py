import pickle
import re
from collections import defaultdict


class MarkovChain(object):
    def __init__(self, input_data):
        self.input_data = input_data
        self.generate_database()

    def generate_database(self):
        self.db = db_factory()
        #text_sample = word_iterator(input_data)
        for sentence in self.input_data:
            words = sentence.strip().split()
            self.db[("",)][words[0]] += 1
            for order in range(1, 3):
                print("NEW ORDER")
                for i in range(len(words) - 1):
                    if i + order >= len(words):
                        continue
                    word = tuple(words[i:i + order])
                    self.db[word][words[i + order]] += 1
                self.db[tuple(words[len(words) - order:len(words)])][""] += 1

                print(self.db)

        pass


def db_factory():
    return defaultdict(one_dict)

def one_dict():
    return defaultdict(one)

def one():
    return 1.0



def word_iterator(sentence):
    # An iterator over the words in the sentence
    splitter = re.compile(" ")
    pos = 0
    for match in splitter.finditer(sentence):
        word = sentence[pos:match.start()].strip()
        if word:
            yield word
        pos = match.start() + 1


if __name__ == "__main__":
    data_file = './patch_data.pickle'
    with open(data_file, "rb") as pickle_file:
        data = pickle.load(pickle_file)
    chain = MarkovChain([data["Balance Changes"][0]])
