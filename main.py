import csv
from datetime import datetime

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

    def __iter__(self):
        return iter(
            [self.company_name, self.street_address, self.locality, self.zip_code, self.telephone, self.company_size,
             self.company_type])

    @staticmethod
    def get_table_title():
        return ['company name', 'street address', 'locality', 'zip code', 'telephone', 'company size',
                'company type']


def retrieve_jobs(num_of_pages):
    date = datetime.today().strftime('%Y-%m-%d')
    with open(f"report/emploi_quebec_{date}.csv", 'w', newline='', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(Job.get_table_title())

        for x in range(num_of_pages):
            page_number = x + 1
            page = requests.get(get_url_for_page(page_number))
            soup = BeautifulSoup(page.text, 'html.parser')
            soup.encode("utf-8")

            job_divs = soup.findAll("table", {"class": "hide-border-hide-padding"})

            for job_div in job_divs:
                job = get_job(job_div)
                writer.writerow(job)

            log_download_progression(page_number, num_of_pages)


def get_job(job_div):
    company_name = job_div.find("strong", {"itemprop": "title"}).get_text()
    street_address = job_div.find("li", {"itemprop": "street-address"}).get_text().strip()
    locality = job_div.find("li", {"itemprop": "locality"}).get_text().strip()
    zip_code = job_div.find("li", {"itemprop": "region"}).get_text().strip()
    telephone = job_div.find("li", {"itemprop": "telephone"}).get_text().strip().replace('Téléphone : ', '')
    company_size = get_company_size(job_div)
    company_type = job_div.find(text=re.compile("\(SCIAN")).strip()
    job = Job(company_name, street_address, locality, zip_code, telephone, company_size, company_type)
    return job


def get_company_size(job_div):
    if job_div.find("li",
                    {"itemprop": "interactionCount"}) is not None:  # The html is not consistent across the website
        company_size = job_div.find("li", {"itemprop": "interactionCount"}).get_text().strip()
    else:
        company_size = job_div.find("li", {"itemprop": "employees"}).get_text().strip()
    return company_size


def get_url_for_page(page_number):
    return f"http://imt.emploiquebec.gouv.qc.ca/mtg/inter/noncache/contenu/asp/ice622_resultrechr_01.asp?entpage={page_number}&entScroll=0&entpagefav=1&empMaxEnt=9999999999999&PT4=54&entrfav=False&PT3=10&entTriFav=01&lang=FRAN&Porte=4&cregn=QC&PT1=8&regnp4=08&empMinEnt=5&PT2=21&fbclid=IwAR0p0wHdCKRACf85lEX0HpR%5F5U0U12%2Dw1ZOnjAzIQTD0KoOJohLe3AGz6DQ&entTri=01&imp=1"


def log_download_progression(page_number, num_of_pages):
    page = 'page'
    if page_number > 1:
        page = 'pages'
    print(f"📄 {page_number} {page} saved out of {num_of_pages}.")


if __name__ == "__main__":
    num_of_pages = calculate_number_of_pages()
    retrieve_jobs(num_of_pages)
