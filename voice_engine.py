import pygsheets
import pandas as pd
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from io import BytesIO
import numpy as np

IMAGE_SET_CSV = "voice_image_set.csv"
AUDIO_PATH = "1vm990mkdtkTPdJcf4cWDO0p9g1WivoXK"

def authenticate():
    credit_dict = json.loads(os.environ.get("GOOGLE_AUTH_INPERSON"))
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_info(credit_dict, scopes=scopes)
    return build('drive', 'v3', credentials=creds)


def get_image_sets():
    images = []
    with open(IMAGE_SET_CSV) as f:
        for line in f:
            images.append(f"/static/images/{line}")
    return images


class voiceEngine:
    """
    This class creates a SQL database named.
    It contains the following tables:
    - demographics: contains the demographics of the workers.
    - jobs: contains the jobs that the workers have completed.
    - workers: contains the workers.
    - ratings: contains the ratings of the workers.
    """
    def __init__(self):
        self.gc = pygsheets.authorize(service_account_env_var="GOOGLE_AUTH_INPERSON")
        self.gdrive = authenticate()
        self.sh = self.gc.open_by_url("https://docs.google.com/spreadsheets/d/11dANYUYq4H-4Toa4hvqpSae_GKvGeeOZcn4kJ7TAjHk/edit?usp=sharing")
        self.image_sets = get_image_sets()
        self.get_worksheets()
    
    def get_worksheets(self):
        self.user_wks = self.sh.worksheet('title','user')
        self.assignmet_wks = self.sh.worksheet('title','assignment')
        self.images_wks = self.sh.worksheet('title','image')
        self.calibrations_wks = self.sh.worksheet('title', 'calibration')

    def check_worker_id(self, worker_id):
        """
        Checks if a worker_id is in the database.
        Returns True if worker is already in database
        """
        user_df = self.user_wks.get_as_df()
        return worker_id in user_df.user_id.values
    
    def check_worker_assignment(self, worker_id, assignment_id):
        """
        Checks if a worker has already completed a task.
        Returns True if assignment and Worker are already in database
        """
        assignment_df = self.assignmet_wks.get_as_df()
        return len(assignment_df[(assignment_df.assignment_id == assignment_id)&(assignment_df.user_id == worker_id)]) > 0

    
    def get_images(self, worker_id):
        """
        Returns the images of a worker.
        """
        np.random.shuffle(self.image_sets)
        return self.image_sets
    
    def save_data(self, data): # worker_id, assignment_id, condition, answers_dict, answer_blobs, demographics, calibrations):
        """
        Saves the data of a worker.
        """
        if self.check_worker_assignment(data['worker_id'], data['assignment_id']):
            return False
        else:
            # Uploading assignment metadata
            assignment = [data['assignment_id'], data['worker_id'], data['condition'], data['medium']]
            self.append_to_table(self.assignmet_wks, assignment)

            # Uploadig worker demographics
            if not self.check_worker_id(data['worker_id']):
                demographics_obj = json.loads(data['demographics'])
                user = [
                    data['worker_id'], 
                    demographics_obj['age-input'], 
                    ";".join(demographics_obj['race-input']),
                    ";".join(demographics_obj['ethnicity-input']),
                    ";".join(demographics_obj['gender-input']),
                    demographics_obj['education-radio'],
                    demographics_obj['english-radio'], 
                    demographics_obj['glasses-radio'],
                    demographics_obj['lenses-radio'], 
                    demographics_obj['colorblind-radio']
                    ]
                self.append_to_table(self.user_wks, user)

            
            # Uploading audio files
            description_paths = {}
            for record_name, blob in data['answer_blobs'].items():
                blob.save("temp.webm")
                media = MediaFileUpload("temp.webm", mimetype=blob.mimetype, resumable=True)
                fmeta = {"name": f"{record_name}.webm", "parents":[AUDIO_PATH]}
                file = self.gdrive.files().create(body=fmeta, media_body=media).execute()
                description_paths[record_name] = f"https://drive.google.com/file/d/{file.get('id')}/view"
                os.remove("temp.webm")
            # Uploading description information
            answer_obj = json.loads(data['answers_dict'])
            answers = []
            for answer in answer_obj:
                if answer['medium'] == "speech":
                    answers.append([
                        data['assignment_id'], 
                        answer['im_url'],
                        answer['im_name'], 
                        "spoken",
                        answer['fname'],
                        description_paths[answer['fname']], 
                        answer['im_time'], 
                        answer['im_start_time'], 
                        answer['im_end_time'],
                        answer['im_width'],
                        answer['im_height']
                        ])
                else:
                    answers.append([
                        data['assignment_id'], 
                        answer['im_url'],
                        answer['im_name'], 
                        "written",
                        "",
                        answer['description'], 
                        answer['im_time'], 
                        answer['im_start_time'], 
                        answer['im_end_time'],
                        answer['im_width'],
                        answer['im_height']
                        ])      
            self.append_to_table(self.images_wks, answers, len(answer_obj))

            # Uploading Calibrations
            cal_obj = json.loads(data['calibrations'])
            cals = []
            for i, cal in enumerate(cal_obj):
                cals.append([
                    data['assignment_id'],
                    i + 1,
                    cal['start'],
                    cal['end']
                ])
            self.append_to_table(self.calibrations_wks, cals, len(cals))
            return True

    def append_to_table(self, wks, values, nv=1):
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        last_row = len(cells)
        wks.insert_rows(last_row, number=nv, values=values)