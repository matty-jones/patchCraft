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
    horoscope_headings = ["Family", "Love", "Friendship", "Career"]
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
    parsed_horoscope = {heading: None for heading in horoscope_headings}
    parsed_table = {heading: None for heading in table_headings}
    print("---=== HOROSCOPE TEXT ===---")
    print(horoscope_text)
    print("---=== TABLE DATA ===---")
    print(table_data)
    exit()


    # Patch notes begin with an H3 so find these first
    # heading_lists = [heading['title'] for heading in parsed_page.findAll('h3')]
    patch_data = {}
    for h2 in parsed_page.findAll("h2"):
        # Skip the left sidebar
        if h2.get_text() == "Contents":
            continue
        try:
            category_title = h2.span.get_text()
        except AttributeError:
            continue
        # Skip the final section
        if category_title == "External Links":
            continue
        for heading in h2.findNextSiblings():
            if heading.name != "h3":
                continue
            heading_title = heading.get_text().split("[edit]")[0]
            # print(heading_title)
            # input('This is a title')
            for next_sibling in heading.findNextSiblings():
                # print(next_sibling)
                # input('This is a sibling. Sibling.name = ' + next_sibling.name)
                # This is for a single bullet point (i.e. general patch notes)
                if next_sibling.name == "ul":
                    heading_title_formatted = " ".join(
                        [word.capitalize() for word in heading_title.split(" ")]
                    )
                    if heading_title_formatted not in patch_data:
                        patch_data[heading_title_formatted] = []
                    next_text = [
                        text
                        for text in next_sibling.get_text().split("\n")
                        if len(text.split(" ")) > 4
                    ]
                    patch_data[heading_title_formatted] += next_text
                # This is for a descriptive list (set of bullet points commonly used for balance changes)
                elif next_sibling.name == "dl":
                    try:
                        full_element = [dl.text for dl in next_sibling][0].split("\n")
                    except AttributeError:
                        # No text element
                        continue
                    if "Units" not in patch_data.keys():
                        patch_data["Units"] = {}
                    for line in full_element:
                        if len(line.split(" ")) == 1:
                            # Only one word, therefore this is the unit name
                            unit_name = line.capitalize()
                            if unit_name not in patch_data["Units"]:
                                patch_data["Units"][unit_name] = []
                                continue
                        try:
                            if (line != unit_name) and (
                                line not in patch_data["Units"][unit_name]
                            ):
                                patch_data["Units"][unit_name].append(line)
                        except UnboundLocalError:
                            # Patch note is not sorted by unit name
                            unit_name = "Misc"
                            if unit_name not in patch_data["Units"]:
                                patch_data["Units"][unit_name] = []
                            if (line != unit_name) and (
                                line not in patch_data["Units"][unit_name]
                            ):
                                patch_data["Units"][unit_name].append(line)
    return patch_data


# TODO: Remove the 'Official Source' and 'STARCRAFT II BALANCE UPDATE.....' lines
# TODO: Fix nested <ul> s.t. we display them as 'New coop commanders: Mira and Matthew Han, Zeratul'

# def get_blank_units_dict():
#    LotVURL = root + '/starcraft2/Units_(Legacy_of_the_Void)'
#    HotSURL = root + '/starcraft2/Units_(Heart_of_the_Swarm)'
#    WoLURL = root + '/starcraft2/Units/WoL'
#    units_dict = {'Protoss': {}, 'Terran': {}, 'Zerg': {}}
#    buildings_dict = {'Protoss': {}, 'Terran': {}, 'Zerg': {}}
#    page = requests.get(LotVURL)
#    parsed_page = BeautifulSoup(page.content, 'html.parser')
#
#    for h2 in parsed_page.findAll('h2'):
#        h2Heading = h2.get_text().split(' ')
#        if len(h2Heading[0]) != 0:
#            continue
#        race = h2Heading[1]
#        print("---=== NEW H2 ===---")
#        print(race)
#        # Gather the section of the page between the headings
#        nextElement = h2
#        while nextElement is not None:
#            nextElement = nextElement.nextSibling
#            try:
#                tagName = nextElement.name
#            except:
#                continue
#            if tagName == 'h2':
#                break
#            elif tagName == 'table':
#                print("---=== NEW H3 ===---")
#                print(nextElement)
#
#
#
#
##            nexth3 = nextElement
##            while nexth3 is not None:
##                nexth3 = nexth3.nextSibling
##                try:
##                    tagName2 = nexth3.name
##                except:
##                    continue
##                if tagName2 == 'h3':
##                    print("---=== NEW H3 ===---")
##                    print(h3.get_text())
##                    nextNode = h3
##                    while nextNode is not None:
##                        nextNode = nextNode.nextSibling
##                        try:
##                            tagName3 = nextNode.name
##                        except:
##                            continue
##                        if tagName3 == 'h3':
##                            break
##                        unorderedList = nextNode.find_next('ul')
##                        print(unorderedList)
##                        for element in unorderedList.findAll('li'):
##                            print("--== New Element ==--")
##                            print(element)
#    exit()
#
#
#
#
#            #for h3 in nextElement.findAll('h3'):
#            #    print("---=== NEW H3 ===---")
#            #    print(h3.get_text())
#            #    nextNode = h3
#            #    while nextNode is not None:
#            #        nextNode = nextNode.nextSibling
#            #        try:
#            #            tagName = nextNode.name
#            #        except:
#            #            continue
#            #        if tagName == 'h3':
#            #            break
#            #        unorderedList = nextNode.find_next('ul')
#            #        print(unorderedList)
#            #        for element in unorderedList.findAll('li'):
#            #            print("--== New Element ==--")
#            #            print(element)
#
#
#
#    for h3 in parsed_page.findAll('h3'):
#        print("---=== NEW H3 ===---")
#        print(h3.get_text())
#        print(h3.find_next('ul'))
#    exit()
#
#
#
#    #for ul in parsed_page.findAll('ul'):
#    #    if ul.li is None:
#    #        continue
#    #    if len(ul.li) == 2:
#    #        print('---=== NEW UL ===---')
#    #        print(ul.li)
#
#
#    # This tries to get the heading names but I can't find a way to jump into the uls after finding the heading I want
#    #for h3 in parsed_page.findAll('h3'):
#    #    print('\n')
#    #    print(h3.span['id'])
#    #    print(h3.findNextSibling())
#    #    exit()


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
