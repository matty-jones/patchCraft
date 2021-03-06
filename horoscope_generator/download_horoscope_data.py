import copy
import datetime
import itertools
import requests
import re
import pickle
import time as T
from bs4 import BeautifulSoup

root = "http://www.0800-horoscope.com/horoscope-archive"
zodiac = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
horoscope_headings = ["Family", "Love", "Friendship", "Career", "Finances"]
table_headings = ["State of Mind", "Karma Numbers", "Buzz Words", "Compatible Sign"]

def obtain_patch_note_links(root_URL):
    first_date = datetime.datetime(2003, 10, 27)
    last_date = datetime.datetime(2011, 12, 31)
    all_dates = []
    previous_date = copy.deepcopy(first_date)
    while True:
        all_dates.append("{:04d}-{:02d}-{:02d}".format(previous_date.year, previous_date.month, previous_date.day))
        next_date = previous_date + datetime.timedelta(days=7)
        if next_date >= last_date:
            break
        previous_date = copy.deepcopy(next_date)
    combinations = itertools.product(zodiac, all_dates)
    links = []
    for [zod_sign, date] in combinations:
        links.append("/".join([root, zod_sign, "weekly", date]))
    return links


def scrape_URL(URL):
    page = requests.get(URL)
    parsed_page = BeautifulSoup(page.content, "html.parser")
    horoscope_data = {heading[:-1]: None for heading in horoscope_headings}
    for h3 in parsed_page.findAll("h3"):
        # Family always comes first!
        if h3.get_text() != "Family:":
            continue
        horoscope_text = []
        for horoscope in h3.findNextSiblings():
            horoscope_text.append(horoscope.get_text())
    for table in parsed_page.findAll("tbody"):
        table_data = table.get_text()
    # Parse the horoscope
    horoscope_list = [
            data for data in horoscope_text if data not in [
                "".join([heading, ":"]) for heading in horoscope_headings
                ]
            ]
    parsed_horoscope = {heading: text for [heading, text] in zip(horoscope_headings, horoscope_list)}
    # Parse the table
    table_list = [
            data for data in table_data.split("\n") if data not in [
                "".join([heading, ":"]) for heading in table_headings
                ]
            and len(data) > 1
            ]
    parsed_table = {heading: text for [heading, text] in zip(table_headings, table_list)}
    return parsed_horoscope, parsed_table


if __name__ == "__main__":
    data_URL = obtain_patch_note_links(root)
    data_URL = sorted(list(set(data_URL)), reverse=True)
    print("Found", len(data_URL), "URLs to parse.")
    data_by_zodiac = {
            zod_sign: {
                "horoscope": {heading: [] for heading in horoscope_headings},
                "table": {heading: [] for heading in table_headings}
                }
            for zod_sign in zodiac
            }
    t0 = T.time()
    for URL_counter, URL in enumerate(data_URL):
        t1 = T.time()
        try:
            print("\rParsing URL {} of {}. Elapsed time = {:.0f} seconds, Remaining time estimate = {:.0f} seconds...".format(URL_counter + 1, len(data_URL), t1 - t0, (t1 - t0) * (len(data_URL) - URL_counter) / URL_counter), end=" ")
        except ZeroDivisionError:
            print("\rParsing URL {} of {}.".format(URL_counter + 1, len(data_URL)), end=" ")
        zod_sign = URL.split("/")[-3]
        parsed_horoscope, parsed_table = scrape_URL(URL)
        for key, val in parsed_horoscope.items():
            data_by_zodiac[zod_sign]["horoscope"][key].append(val)
        for key, val in parsed_table.items():
            data_by_zodiac[zod_sign]["table"][key].append(val)
    # for zod_sign in zodiac:
    #     complete_horoscope_data = {heading: [] for heading in horoscope_headings}
    #     complete_table_data = {heading: [] for heading in table_headings}
    #     for URL in data_URL:
    #         print("\rParsing URL {} of {} ({})...".format(URL_counter + 1, len(data_URL), URL), end=" ")
    #         if zod_sign not in URL:
    #             continue
    #         URL_counter += 1
    #         parsed_horoscope, parsed_table = scrape_URL(URL)
    #         for key, val in parsed_horoscope.items():
    #             complete_horoscope_data[key].append(val)
    #         for key, val in parsed_table.items():
    #             complete_table_data[key].append(val)
    #     data_by_zodiac[zod_sign]["horoscope"] = complete_horoscope_data
    #     data_by_zodiac[zod_sign]["table"] = complete_table_data
    with open("horoscope_data.pickle", "wb+") as pickle_file:
        pickle.dump(data_by_zodiac, pickle_file)
