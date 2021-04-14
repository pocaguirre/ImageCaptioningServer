import numpy as np
from queue import Queue

# CONSTANTS
ROOT = "https://imagecaptioningicl.azurewebsites.net/"
STATIC_ROOT = f"{ROOT}static/"

IMAGE_SETS = {
    "test1": [f"{STATIC_ROOT}images/{img}" for img in ['dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg']],
    "test2": [f"{STATIC_ROOT}images/{img}" for img in ['dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg']],
    "test3": [f"{STATIC_ROOT}images/{img}" for img in ['dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg']],
    "test4": [f"{STATIC_ROOT}images/{img}" for img in ['dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg', 'dog.jpg', 'cat.jpg']],
}


def real_task(func):

    def inner(self, worker_id, assign_id):
        task = func(self, worker_id, assign_id)
        if 'condition' not in task:
            return {"ERROR"}
        task_obj = {
            "html": f"{ROOT}condition/{task['condition']} #main-body",
            "js": f"{STATIC_ROOT}js/{task['condition']}.js",
            "images": IMAGE_SETS[task['images']]
        }
        return task_obj
    return inner


class Assignment(object):
    def __init__(self, assign_id, worker_id=None, task: dict = None):
        self.worker_id = worker_id
        self._task = task
        self.id = assign_id
        self.answer = None

    @property
    def task(self) -> dict:
        return self._task

    def __eq__(self, other):
        if not isinstance(other, Assignment):
            # assume it's string id
            return self.id == other
        return self.id == other.id


class Tasks(object):
    def __init__(self, cap_per_img=3):
        self.workers = {}
        self.cap_per_img = cap_per_img
        self.jobs = np.zeros((4, 4))
        self.conditions = ['control', 'time', 'essential', 'comprehensive']
        self.images = list(IMAGE_SETS.keys())
        self.assignments = []

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
        self.workers[worker_id] = {"queue": q, "assignments": []}
        return

    def _check_worker_exists(self, worker_id) -> bool:
        return worker_id in self.workers

    def _check_valid_worker(self, worker_id) -> bool:
        if self._check_worker_exists(worker_id):
            return not self.workers[worker_id]['queue'].empty()
        return True

    def _is_new_assignment(self, assign_id) -> bool:
        """
        Returns True if this is a new assignment for worker id (being robust against
        reloading on client side)
        :param assign_id:
        :return:
        """
        return assign_id not in self.assignments

    def save_anwer(self, assign_id, answer):
        for a in self.assignments:
            if a.id == assign_id:
                a.answer = answer
                return True
        return False

    @real_task
    def get_task(self, worker_id, assign_id) -> dict:
        if not self._check_worker_exists(worker_id):
            self._set_up_worker(worker_id)
        if self._is_new_assignment(assign_id):
            if self._check_valid_worker(worker_id):
                # Get Task
                task = self.workers[worker_id]['queue'].get()
                self._update_jobs_assigned(task['condition'], task['images'])

                # Get new Assignment
                a = Assignment(assign_id, worker_id=worker_id, task=task)
                self.assignments.append(a)
                self.workers[worker_id]['assignments'].append(a)
                return task
            else:
                return {"return": "all jobs done"}
        else:
            for assign in self.assignments:
                if assign.id == assign_id:
                    return assign.task

    def get_test_task(self, worker_id):
        if not self._check_worker_exists(worker_id):
            self._set_up_worker(worker_id)
        if self._check_valid_worker(worker_id):
            # Get Task
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
        aid = input("Assgin ID: ")
        task = tasks.get_task(wid, aid)
        print(task)
        cont = input("continue? Y/N")
        if cont[0] == 'N':
            flag = False
