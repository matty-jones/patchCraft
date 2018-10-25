import pickle
import re
from collections import defaultdict


class MarkovChain(object):
    def __init__(self, input_data):
        self.input_data = input_data
        self.generate_database()

    def generate_database(self, n_words=2):
        # Set up a blank database, which is a defaultdict
        # where empty values are set to 1.0
        self.db = create_database()
        for sentence in self.input_data:
            words = sentence.strip().split()
            self.db[("",)][words[0]] += 1
            for order in range(1, n_words):
                # n_words controls the number of words to look at
                # when assigning the order probabilities in the chain.
                # The larger the number, the more sense the generated
                # sentence will make, but the higher the probability
                # the chain regurgitates a sentence that already exists.
                for i in range(len(words) - 1):
                    if i + order >= len(words):
                        continue
                    word = tuple(words[i:i + order])
                    self.db[word][words[i + order]] += 1
                self.db[tuple(words[len(words) - order:len(words)])][""] += 1
        # Database now has word frequencies, change these to probabilities
        for word in self.db:
            word_freq = 0
            for next_word in self.db[word]:
                word_freq += self.db[word][next_word]
            if word_freq > 0:
                for next_word in self.db[word]:
                    self.db[word][next_word] /= word_freq

    def generate_sentence(self):
        # Now the fun bit! Need to pick words based on the probabilities
        # and the order.
        # At first, the sentence is empty.
        sentence = []
        next_word = self.get_next_word(("",))
        while next_word:
            sentence.append(next_word)
            next_word = self.get_next_word(sentence)
        return " ".join(sentence).strip()


    def get_next_word(self, previous_word):
        pass

def create_database():
    # Create a dictionary where non-specified word chains have
    # a default value that is a defaultdict that returns 1 for
    # none-specified words.
    return defaultdict(one_dict)

def one_dict():
    # Create a dictionary where non-specified word keys have
    # a default value of one.
    return defaultdict(one)

def one():
    # Defaultdict requires a callable, so create a function
    # that just returns 1.0
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
