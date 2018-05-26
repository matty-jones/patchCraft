import requests
import re
from bs4 import BeautifulSoup

root = 'http://liquipedia.net'

def obtain_patch_note_links(URL):
    page = requests.get(URL)
    parsed_page = BeautifulSoup(page.content, 'html.parser')
    links = [link['href'] for link in parsed_page.findAll(title=re.compile('^Patch '), href=re.compile('^((?!#).)*$'))]
    return links


def scrape_patches(URL):
    print('Parsing', URL)
    page = requests.get(URL)
    parsed_page = BeautifulSoup(page.content, 'html.parser')
    #print(parsed_page)
    # Patch notes begin with an H3 so find these first
    #heading_lists = [heading['title'] for heading in parsed_page.findAll('h3')]
    patch_data = {}
    for h2 in parsed_page.findAll('h2'):
        # Skip the left sidebar
        if h2.get_text() == 'Contents':
            continue
        category_title = h2.span.get_text()
        # Skip the final section
        if category_title == 'External Links':
            continue
        for heading in h2.findNextSiblings():
            if heading.name != 'h3':
                continue
            heading_title = heading.get_text().split('[edit]')[0]
            #print(heading_title)
            #input('This is a title')
            for next_sibling in heading.findNextSiblings():
                #print(next_sibling)
                #input('This is a sibling. Sibling.name = ' + next_sibling.name)
                # This is for a single bullet point (i.e. general patch notes)
                if next_sibling.name == 'ul':
                    if heading_title not in patch_data:
                        patch_data[heading_title] = []
                    patch_data[heading_title] += next_sibling.get_text().split('\n')
                # This is for a descriptive list (set of bullet points commonly used for balance changes)
                elif next_sibling.name == 'dl':
                    print([dl.text for dl in next_sibling][0])
                    exit()
                    print(dir(next_sibling))
                    print(next_sibling.prettify())
                    input('^^^ DL Sibling text')

    for key, val in patch_data.items():
        print('\n')
        print(key, val)
    input('Completed one...')
    return patch_data


# TODO: Remove the 'Official Source' and 'STARCRAFT II BALANCE UPDATE.....' lines
# TODO: Fix nested <ul> s.t. we display them as 'New coop commanders: Mira and Matthew Han, Zeratul'

#def get_blank_units_dict():
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
    patch_links = obtain_patch_note_links(root + '/starcraft2/Patches')
    complete_patch_data = {}
    for patch_link in patch_links:
        patch_data = scrape_patches(root + patch_link)
        for key, val in patch_data.items():
            if key not in complete_patch_data:
                complete_patch_data[key] = []
            complete_patch_data[key] += val

