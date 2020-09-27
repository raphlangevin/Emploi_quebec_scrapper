import csv
import os
from abc import ABC, abstractmethod
from datetime import datetime

from boxsdk import OAuth2, Client
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from emploi_quebec_2 import config
from enum import Enum, auto

REPORT_PATH = 'report'


class JobSaverType(Enum):
    LOCAL = auto()
    GOOGLE_DRIVE = auto()
    BOX = auto()


class JobSaver(ABC):
    @abstractmethod
    def save_job_offers(self, job_offers):
        pass


class LocalJobSaver(JobSaver):
    def save_job_offers(self, job_offers):
        date = datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
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


class BoxJobSaver(JobSaver):

    def __init__(self):
        oauth = OAuth2(
            client_id=config.BOX_CLIENT_ID,
            client_secret=config.BOX_CLIENT_SECRET,
            access_token=config.BOX_ACCESS_TOKEN,
        )
        self.client = Client(oauth)
        self.local_job_saver = LocalJobSaver()
        self.root_folder = self.client.folder(folder_id='0')

    def save_job_offers(self, job_offers) -> str:
        file_name = self.local_job_saver.save_job_offers(job_offers)
        folder = self.create_folder_if_not_exist(REPORT_PATH)
        uploaded_file = folder.upload(file_name)
        return uploaded_file.get_shared_link()

    def create_folder_if_not_exist(self, folder_path):
        folder_exist, folder = self.folder_exist(folder_path)
        if folder_exist:
            return folder
        else:
            return self.root_folder.create_subfolder(folder_path)

    def folder_exist(self, folder_path):
        folders = self.root_folder.get_items()
        for folder in folders:
            if folder.type.capitalize() == 'Folder' and folder.name == folder_path:
                return True, self.client.folder(folder_id=folder.id)
        return False, None


def get_job_saver(job_saver_type: JobSaverType) -> JobSaver:
    if job_saver_type == JobSaverType.LOCAL:
        return LocalJobSaver()
    elif job_saver_type == JobSaverType.GOOGLE_DRIVE:
        return GoogleDriveJobSaver()
    elif job_saver_type == JobSaverType.BOX:
        return BoxJobSaver()
