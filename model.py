import numpy as np


class Tasks(object):
    def __init__(self, cap_per_img=3):
        self.workers = []
        self.cap_per_img = cap_per_img
        self.jobs = np.zeros((4, 4))
        self.conditions = ['control', 'time', 'essential', 'comprehensive']
        self.images = ['A', 'B', 'C', 'D']
        self.results = []
        self.wrk2cond = {}
        self.wrk2img = {}

    def worker_to_condition(self, worker_id):
        if worker_id not in self.wrk2cond:
            self.wrk2cond[worker_id] = []
        return self.wrk2cond[worker_id]

    def worker_to_image(self, worker_id):
        if worker_id not in self.wrk2img:
            self.wrk2img[worker_id] = []
        return self.wrk2img[worker_id]

    def get_task(self, worker_id):
        valid = False
        count = 0
        while not valid:
            condition_done = self.worker_to_condition(worker_id)
            cond_avail = list(set(self.conditions) - set(condition_done))
            condition = np.random.choice(cond_avail)

            image_done = self.worker_to_image(worker_id)
            img_avail = list(set(self.images) - set(image_done))
            image = np.random.choice(img_avail)
            valid = self.jobs[self.conditions.index(condition), self.images.index(image)] < self.cap_per_img
            count = 4 - len(cond_avail)






