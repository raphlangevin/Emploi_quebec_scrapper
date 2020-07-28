import math
import re

import requests
from bs4 import BeautifulSoup

URL = 'http://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/listoffr.asp?mtcle=&offrdisptoutqc=2&pp=1&prov=http' \
      '%3A%2F%2Fplacement%2Eemploiquebec%2Egouv%2Eqc%2Eca%2Fmbe%2Fut%2Frechroffr%2Frechrcle%2Easp%3Fmtcle%3D%26pp%3D1' \
      '%26prov%3Dhttp%253A%252F%252Fplacement%252Eemploiquebec%252Egouv%252Eqc%252Eca%252Fmbe%252Fut%252Frechroffr' \
      '%252Ferechroffr%252Easp%26date%3D3%26creg%3D08&date=3&creg=08&NO%5FPAGE=1&CL=french'


def calculate_number_of_pages() -> int:
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    number_of_job_offers = get_number_of_job_offers(soup)
    number_of_job_offers_per_page = get_number_of_job_offers_per_page(soup)
    return math.ceil(number_of_job_offers / number_of_job_offers_per_page)


def get_number_of_job_offers_per_page(soup):
    return len(soup.find("table", {"class": "donnees"}).find("tbody").findAll("tr"))


def get_number_of_job_offers(soup):
    elements = soup.select(".contenu")[0].contents
    pattern = 'offre\(s\) trouvée\(s\) : ([0-9]+)'
    for element in elements:
        element = str(element).strip()
        if re.search(pattern, element):
            return int(re.search(pattern, element).group(1))


if __name__ == "__main__":
    number_of_pages = calculate_number_of_pages()
    print(number_of_pages)
