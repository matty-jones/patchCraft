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
    print("Parsing", URL)
    page = requests.get(URL)
    parsed_page = BeautifulSoup(page.content, "html.parser")
    horoscope_headings = ["Family", "Love", "Friendship", "Career", "Finances"]
    table_headings = ["State of Mind", "Karma Numbers", "Buzz Words", "Compatible Sign"]
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
    print("Found", len(data_URL), "patch links to parse.")
    complete_data = {}
    for URL in data_URL:
        wobbey = scrape_URL(URL)




    exit()
    while True:
        patch_data = scrape_patches(root + patch_link)
        for key, val in patch_data.items():
            if key not in complete_patch_data:
                if type(val) is not dict:
                    complete_patch_data[key] = []
                else:
                    complete_patch_data[key] = {}
            if type(val) is not dict:
                complete_patch_data[key] += val
            else:
                for key2, val2 in val.items():
                    if key2 not in complete_patch_data[key]:
                        complete_patch_data[key][key2] = []
                    complete_patch_data[key][key2].append(val2)
    with open("patch_data.pickle", "wb+") as pickle_file:
        pickle.dump(complete_patch_data, pickle_file)
