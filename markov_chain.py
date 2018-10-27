import argparse
import pickle
import re
import random as R
from collections import defaultdict


class MarkovChain(object):
    def __init__(self, input_data, n_words=2):
        self.input_data = input_data
        self.generate_database(n_words)

    def generate_database(self, n_words):
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
                    word = tuple(words[i : i + order])
                    self.db[word][words[i + order]] += 1
                self.db[tuple(words[len(words) - order : len(words)])][""] += 1
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

    def get_next_word(self, previous):
        previous = tuple(previous)
        if previous != ("",):
            while previous not in self.db:
                previous = previous[1:]
                if not previous:
                    return ""
        probabilities = self.db[previous]
        probability = R.random()
        max_prob = 0.0
        max_prob_word = ""
        for candidate in probabilities:
            new_probability = probabilities[candidate]
            if new_probability > max_prob:
                max_prob = new_probability
                max_prob_word = candidate
            if probability > new_probability:
                probability -= new_probability
            else:
                return candidate
        # Otherwise, return maximum probability match
        return max_prob_word


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
        word = sentence[pos : match.start()].strip()
        if word:
            yield word
        pos = match.start() + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="PatchCraft", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-n",
        "--n_sentences",
        type=int,
        default=10,
        required=False,
        help="""The number of non-input sentences to generate.""",
    )
    parser.add_argument(
        "-w",
        "--n_words",
        type=int,
        default=4,
        required=False,
        help="""The number of words to consider when deciding
                        order probabilities. A larger value results in more
                        accurate sentences, but less generation (higher chance
                        of repeating input sentences).""",
    )
    parser.add_argument(
        "-c",
        "--category",
        type=str,
        default="all",
        required=False,
        help="""Use to select a category of sentences
                        to output. Good choices are "general", "balance changes",
                        "bug fixes", "co-op missions", and any of the starcraft
                        races.""",
    )
    parser.add_argument(
        "-l",
        "--min_sentence_len",
        type=int,
        default=5,
        required=False,
        help="""Generated sentences must contain at least this
                        many words.""",
    )
    args = parser.parse_args()
    data_file = "./patch_data.pickle"
    with open(data_file, "rb") as pickle_file:
        original_data = pickle.load(pickle_file)
    data = {}
    for key, val in original_data.items():
        data[key.lower()] = val
    if args.category != "all":
        try:
            data_to_use = data[args.category]
        except:
            print("Category", args.category, "not found. Using 'all' instead...")
            data_to_use = [
                sentence
                for value in data.values()
                for sentence in value
                if len(sentence) > 10
            ]
    else:
        data_to_use = [
            sentence
            for value in data.values()
            for sentence in value
            if len(sentence) > 10
        ]
    chain = MarkovChain(data_to_use, n_words=args.n_words)
    generated_sentences = 0
    while generated_sentences < args.n_sentences:
        new_sentence = chain.generate_sentence()
        if (len(new_sentence.split()) < args.min_sentence_len) or (
            new_sentence in data_to_use
        ):
            continue
        else:
            print(new_sentence)
            generated_sentences += 1
