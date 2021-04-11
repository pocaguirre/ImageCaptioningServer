import numpy as np
from queue import Queue


class Tasks(object):
    def __init__(self, cap_per_img=3):
        self.workers = {}
        self.cap_per_img = cap_per_img
        self.jobs = np.zeros((4, 4))
        self.conditions = ['control', 'time', 'essential', 'comprehensive']
        self.images = ['A', 'B', 'C', 'D']

    def _update_jobs_assigned(self, cond, img):
        self.jobs[self.conditions.index(cond), self.images.index(img)] += 1

    def _set_up_worker(self, worker_id):
        c = self.conditions.copy()
        i = self.images.copy()
        q = Queue()
        np.random.shuffle(c)
        np.random.shuffle(i)
        for condition, image_set in zip(c, i):
            q.put({"condition": condition, "images": image_set})
        self.workers[worker_id] = {"queue": q}
        return

    def _check_worker_exists(self, worker_id) -> bool:
        return worker_id in self.workers

    def _check_valid_worker(self, worker_id) -> bool:
        if self._check_worker_exists(worker_id):
            return not self.workers[worker_id]['queue'].empty()
        return True

    def get_task(self, worker_id) -> dict:
        if not self._check_worker_exists(worker_id):
            self._set_up_worker(worker_id)
        if self._check_valid_worker(worker_id):
            task = self.workers[worker_id]['queue'].get()
            self._update_jobs_assigned(task['condition'], task['images'])
            return task
        else:
            return {"return": "all jobs done"}


if __name__ == '__main__':
    tasks = Tasks()
    flag = True
    while flag:
        wid = input("Worker ID: ")
        task = tasks.get_task(wid)
        print(task)
        cont = input("continue? Y/N")
        if cont[0] == 'N':
            flag = False