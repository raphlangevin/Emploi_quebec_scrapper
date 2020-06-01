import requests
import math
from lxml import html

URL = 'http://imt.emploiquebec.gouv.qc.ca/mtg/inter/noncache/contenu/asp/ice622_resultrechr_01.asp?entScroll=0&entpagefav=1&empMaxEnt=9999999999999&PT4=54&PT3=10&entTriFav=01&lang=FRAN&Porte=4&cregn=QC&PT1=8&regnp4=08&empMinEnt=5&PT2=21&fbclid=IwAR0p0wHdCKRACf85lEX0HpR%5F5U0U12%2Dw1ZOnjAzIQTD0KoOJohLe3AGz6DQ'


def calculate_number_of_pages():
    r = requests.get(URL)
    tree = html.fromstring(r.content)
    number_of_company = int(tree.xpath('//h3[@class="sousTitre"]/text()')[0].strip())
    return math.ceil(number_of_company / 10)


if __name__ == "__main__":
    # count the number of webpage
    num_of_pages = calculate_number_of_pages()
    print(num_of_pages)
