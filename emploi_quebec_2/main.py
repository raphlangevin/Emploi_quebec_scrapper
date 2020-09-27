import math
import math
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from emploi_quebec_2.job_saver import get_job_saver, JobSaverType
from log_util import log_download_progression


@dataclass
class JobOffer:
    job_offer_number: int
    job_name: str
    company: str
    number_of_job: int
    level_of_education: str
    years_of_experience: str
    location: str

    def __iter__(self):
        return iter(
            [self.job_offer_number, self.job_name, self.company, self.number_of_job, self.level_of_education,
             self.years_of_experience,
             self.location])


def get_url(page_number):
    return f"http://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/listoffr.asp?mtcle=&offrdisptoutqc=2&pp=1&prov=http%3A%2F%2Fplacement%2Eemploiquebec%2Egouv%2Eqc%2Eca%2Fmbe%2Fut%2Frechroffr%2Frechrcle%2Easp%3Fmtcle%3D%26pp%3D1%26prov%3Dhttp%253A%252F%252Fplacement%252Eemploiquebec%252Egouv%252Eqc%252Eca%252Fmbe%252Fut%252Frechroffr%252Ferechroffr%252Easp%26date%3D3%26creg%3D08&date=3&creg=08&NO%5FPAGE={page_number}&CL=french"


def calculate_number_of_pages() -> int:
    page = requests.get(get_url(1))
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


def get_all_jobs(number_of_pages):
    job_offers = []
    for page_number in range(number_of_pages):
        page_number = page_number + 1

        page = requests.get(get_url(page_number), timeout=15)
        soup = BeautifulSoup(page.text, 'html.parser')
        table_rows = soup.find("table", {"class": "donnees"}).find("tbody").findAll("tr")

        for table_row in table_rows:
            table_line = table_row.findAll("td")
            job_offer = JobOffer(int(table_line[0].text), table_line[1].text, table_line[2].text,
                                 int(table_line[3].text), table_line[4].text, table_line[5].text, table_line[6].text)
            job_offers.append(job_offer)
        log_download_progression(page_number, number_of_pages)
    return job_offers


if __name__ == "__main__":
    number_of_pages = calculate_number_of_pages()
    job_offers = get_all_jobs(number_of_pages)
    job_saver = get_job_saver(JobSaverType.BOX)
    job_saver.save_job_offers(job_offers)
