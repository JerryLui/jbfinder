from bs4 import BeautifulSoup
import requests

wiki = r'https://sv.wikipedia.org/wiki/Lista_%C3%B6ver_st%C3%A4der_i_Sverige'
out = 'swedish_cities.txt'

page = requests.get(wiki, verify=False)

soup = BeautifulSoup(page.content, 'html.parser')

