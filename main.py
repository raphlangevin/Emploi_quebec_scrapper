import requests
import math
from bs4 import BeautifulSoup
import re
from lxml import html

URL = 'http://imt.emploiquebec.gouv.qc.ca/mtg/inter/noncache/contenu/asp/ice622_resultrechr_01.asp?entScroll=0&entpagefav=1&empMaxEnt=9999999999999&PT4=54&PT3=10&entTriFav=01&lang=FRAN&Porte=4&cregn=QC&PT1=8&regnp4=08&empMinEnt=5&PT2=21&fbclid=IwAR0p0wHdCKRACf85lEX0HpR%5F5U0U12%2Dw1ZOnjAzIQTD0KoOJohLe3AGz6DQ'


def calculate_number_of_pages():
    r = requests.get(URL)
    tree = html.fromstring(r.content)
    number_of_company = int(tree.xpath('//h3[@class="sousTitre"]/text()')[0].strip())
    return math.ceil(number_of_company / 10)


class Job:
    def __init__(self, company_name, street_address, locality, zip_code, telephone, company_size, company_type):
        self.company_name = company_name
        self.street_address = street_address
        self.locality = locality
        self.zip_code = zip_code
        self.telephone = telephone
        self.company_size = company_size
        self.company_type = company_type


def retrieve_jobs():
    page = requests.get(URL + '&imp=1')
    soup = BeautifulSoup(page.text, 'html.parser')
    my_divs = soup.findAll("table", {"class": "hide-border-hide-padding"})

    company_name = my_divs[0].find("strong", {"itemprop": "title"}).get_text()
    street_address = my_divs[0].find("li", {"itemprop": "street-address"}).get_text().strip()
    locality = my_divs[0].find("li", {"itemprop": "locality"}).get_text().strip()
    zip_code = my_divs[0].find("li", {"itemprop": "region"}).get_text().strip()
    telephone = my_divs[0].find("li", {"itemprop": "telephone"}).get_text().strip().replace('Téléphone : ', '')
    company_size = my_divs[0].find("li", {"itemprop": "interactionCount"}).get_text().strip()
    company_type = my_divs[0].find(text=re.compile("\(SCIAN")).strip()

    job = Job(company_name, street_address, locality, zip_code, telephone, company_size, company_type)

    return job


if __name__ == "__main__":
    # count the number of webpage
    num_of_pages = calculate_number_of_pages()

    retrieve_jobs()
