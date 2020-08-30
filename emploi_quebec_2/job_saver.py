import csv
import os
from abc import ABC, abstractmethod
from datetime import datetime

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

REPORT_PATH = 'report'


class JobSaver(ABC):
    @abstractmethod
    def save_job_offers(self, job_offers):
        pass


class LocalJobSaver(JobSaver):
    def save_job_offers(self, job_offers):
        date = datetime.today().strftime('%Y-%m-%d')
        if not os.path.exists(REPORT_PATH):
            os.makedirs(REPORT_PATH)
        file_name = f"{REPORT_PATH}/emploi_quebec_{date}.csv"
        with open(file_name, 'w+', newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')

            writer.writerow(
                ['job_offer_number', 'job_name', 'company', 'number_of_job', 'level_of_education',
                 'years_of_experience',
                 'location'])

            for job_offer in job_offers:
                writer.writerow(job_offer)
        return file_name


class GoogleDriveJobSaver(JobSaver):
    def save_job_offers(self, job_offers):
        local_job_saver = LocalJobSaver()
        file_name = local_job_saver.save_job_offers(job_offers)
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        file = drive.CreateFile()
        file.SetContentFile(file_name)
        file.Upload()


def get_job_saver(type):
    if type == 'local':
        return LocalJobSaver()
    elif type == 'googleDrive':
        return GoogleDriveJobSaver()
