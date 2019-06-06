import argparse
import datetime
import pickle
import re
import random as R
from collections import defaultdict

zodiac_signs = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
        "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
        ]
horoscope_headings = ["Family", "Love", "Friendship", "Career", "Finances"]
table_headings = ["State of Mind", "Karma Numbers", "Buzz Words", "Compatible Sign"]

class MarkovChain(object):
    def __init__(self, input_data, n_words=2):
        self.input_data = input_data
        self.all_categories = horoscope_headings + table_headings
        self.generate_database(n_words)

    def generate_database(self, n_words):
        # Set up a blank database, which is a defaultdict
        # where empty values are set to 1.0
        self.db = {}
        for category in self.all_categories:
            self.db[category] = create_database()
            if category in horoscope_headings:
                parent_category = "horoscope"
            else:
                parent_category = "table"
            for sentence in self.input_data[parent_category][category]:
                words = sentence.strip().split()
                try:
                    self.db[category][("",)][words[0]] += 1
                except IndexError:
                    # Empty string in data
                    continue
                for order in range(n_words):
                    # n_words controls the number of words to look at
                    # when assigning the order probabilities in the chain.
                    # The larger the number, the more sense the generated
                    # sentence will make, but the higher the probability
                    # the chain regurgitates a sentence that already exists.
                    for i in range(len(words) - 1):
                        if i + order >= len(words):
                            continue
                        word = tuple(words[i : i + order])
                        self.db[category][word][words[i + order]] += 1
                    self.db[category][tuple(words[len(words) - order : len(words)])][""] += 1
            # Database now has word frequencies, change these to probabilities
            for word in self.db[category]:
                word_freq = 0
                for next_word in self.db[category][word]:
                    word_freq += self.db[category][word][next_word]
                if word_freq > 0:
                    for next_word in self.db[category][word]:
                        self.db[category][word][next_word] /= word_freq

    def generate_horoscope(self):
        # Now the fun bit! Need to pick words based on the probabilities
        # and the order.
        # At first, the sentence is empty.
        sentences = []
        for category in self.all_categories:
            sentence = ["".join(["\n---=== ", category, " ===---", "\n"])]
            next_word = self.get_next_word(("",), category)
            while next_word:
                sentence.append(next_word)
                next_word = self.get_next_word(sentence, category)
            sentences.append(" ".join(sentence).strip())
        return sentences

    def get_next_word(self, previous, category):
        previous = tuple(previous)
        if previous != ("",):
            while previous not in self.db[category]:
                previous = previous[1:]
                if not previous:
                    return ""
        probabilities = self.db[category][previous]
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
        prog="HoroCraft", formatter_class=argparse.ArgumentDefaultsHelpFormatter
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
        "-z",
        "--zodiac",
        type=str,
        default="gemini",
        required=False,
        help="""Use to select a zodiac sign.""",
    )
    args = parser.parse_args()
    data_file = "./horoscope_data.pickle"
    with open(data_file, "rb") as pickle_file:
        original_data = pickle.load(pickle_file)
    data = {}
    for key, val in original_data.items():
        data[key.lower()] = val
    if args.zodiac not in zodiac_signs:
        print("Zodiac", args.zodiac, "not found. Using 'gemini' instead...")
        args.zodiac = "gemini"
    data_to_use = data[args.zodiac]
    chain = MarkovChain(data_to_use, n_words=args.n_words)
    new_horoscope = chain.generate_horoscope()
    print(
            "\n\n-----===== LUDICROUSLY PERSONALISED AND ACCURATE HOROSCOPE FOR {} ON {} =====-----\n\n".format(
                args.zodiac.upper(), datetime.datetime.today().strftime("%d/%m/%y")
                )
            )
    for words in new_horoscope:
        print(words, "\n")
