import requests
import re
from bs4 import BeautifulSoup

root = 'http://wiki.teamliquid.net/'


def obtain_patch_note_links(URL):
    page = requests.get(URL)
    parsed_page = BeautifulSoup(page.content, 'html.parser')
    links = [link for link in parsed_page.findAll(title=re.compile('^Patch '), href=re.compile('^((?!#).)*$'))]
    return links


if __name__ == "__main__":
    patch_links = obtain_patch_note_links(root + 'starcraft2/Patches')
