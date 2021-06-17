import numpy as np
from queue import Queue
import json
import pandas as pd
from typing import List, Dict

IMAGE_SET_CSV = "image_sets.csv"

# CONSTANTS
ROOT = "https://imagecaptioningicl.azurewebsites.net/"
STATIC_ROOT = f"{ROOT}static/"

# TODO: save demographics per assignment (in case workers change answers)


def get_image_sets() -> dict:
    image_set_df = pd.read_csv(IMAGE_SET_CSV)
    image_set_dict = {}
    for i, row in image_set_df.iterrows():
        if row['image set'] in image_set_dict:
            image_set_dict[row['image set']].append(f"{STATIC_ROOT}images/{row['filename']}")
        else:
            image_set_dict[row['image set']] = [f"{STATIC_ROOT}images/{row['filename']}"]
    for image_set, images in image_set_dict.items():
        assert len(images) == 6, "CSV not fell formatted"
    return image_set_dict


IMAGE_SETS = get_image_sets()


def real_task(func):

    def inner(*args):
        task = func(*args)
        if 'condition' not in task:
            return {"ERROR"}
        task_obj = {
            "html": f"{ROOT}interaction/{task['condition']} #main-body",
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

    def update_task(self, new_data: dict) -> None:
        if new_data is not None:
            self._task.update(new_data)
        return

    def __eq__(self, other):
        if not isinstance(other, Assignment):
            # assume it's string id
            return self.id == other
        return self.id == other.id

    def __dict__(self):
        copy = self._task.copy()
        copy.update({
            "id": self.id,
            "condition": self._task['condition'],
            "imageset": self._task['images'],
            "results": self.get_answers(),
            "worker": self.worker_id
        })
        return copy

    def is_answered(self) -> bool:
        """
        Returns true if assignment is completed
        :return:
        """
        return self.answer is not None

    def get_answers(self):
        if not self.is_answered():
            return "NO RESULTS"
        answers = []
        for a in self.answer:
            if 'im_time' in a:
                time = a['im_time']
            else:
                time = -1
            answers.append({
                "description": a['description'],
                "image": a['im_url'],
                "time": time
            })
        return answers

    def to_dict(self):
        copy = self._task.copy()
        copy.update({
            "id": self.id,
            "condition": self._task['condition'],
            "imageset": self._task['images'],
            "results": self.get_answers(),
            "worker": self.worker_id
        })
        return copy


class Worker(object):
    def __init__(self, worker_id, test=False):
        self.worker_id = worker_id
        self.age = None
        self.colorblind = None
        self.education = None
        self.glasses = None
        self.test = test
        self.queue = Queue()
        self.assignments = []

    def update_assignments(self, assignment: Assignment):
        self.assignments.append(assignment.id)

    def update_demographics(self, demographics: Dict=None) -> None:
        if demographics is not {} and 'age-input' in demographics:
            self.age = demographics['age-input']
            self.colorblind = demographics['colorblind-radio']
            self.education = demographics['education-radio']
            self.glasses = demographics['glasses-radio']


class Tasks(object):
    def __init__(self, cap_per_img=3):
        self.workers: List[Worker] = []
        self.cap_per_img = cap_per_img
        self.jobs = np.zeros((4, 4))
        self.conditions = ['control', 'time', 'essential', 'comprehensive']
        self.images = list(IMAGE_SETS.keys())
        self.assignments: List[Assignment] = []

    def _update_jobs_assigned(self, cond, img) -> None:
        self.jobs[self.conditions.index(cond), self.images.index(img)] += 1

    def _set_up_worker(self, worker_id, test=False) -> None:
        if not test:
            worker = Worker(worker_id, test)

            c = self.conditions.copy()
            i = self.images.copy()
            np.random.shuffle(c)
            np.random.shuffle(i)

            for condition, image_set in zip(c, i):
                worker.queue.put({"condition": condition, "images": image_set})
            self.workers.append(worker)
            return
        else:
            worker = Worker(worker_id, test)
            self.workers.append(worker)
            return

    def _check_worker_exists(self, worker_id) -> bool:
        for w in self.workers:
            if w.worker_id == worker_id:
                return True
        return False

    def _get_worker(self, worker_id) -> Worker:
        for w in self.workers:
            if w.worker_id == worker_id:
                return w
        raise Exception("Worker Not Found Error")

    def _check_valid_worker(self, worker_id) -> bool:
        if self._check_worker_exists(worker_id):
            worker = self._get_worker(worker_id)
            if worker.test:
                return True
            return not worker.queue.empty()
        return True

    def _is_test_worker(self, worker_id) -> bool:
        if self._check_worker_exists(worker_id):
            worker = self._get_worker(worker_id)
            return not worker.test
        return False

    def _is_new_assignment(self, assign_id) -> bool:
        """
        Returns True if this is a new assignment for worker id (being robust against
        reloading on client side)
        :param assign_id:
        :return:
        """
        return assign_id not in self.assignments

    def _update_worker_id(self, old_id, new_id):
        for worker in self.workers:
            if worker.worker_id == old_id:
                worker.worker_id = new_id
        self._set_up_worker(new_id)

    def output_jobs(self):
        output = {'images': self.images}
        rows = []
        for i, condition in enumerate(self.conditions):
            rows.append({"condition": condition, "data": self.jobs[i].tolist()})
        output['rows'] = rows
        return output

    def get_workers(self):
        workers = []
        for worker in self.workers:
            worker_obj = {"id": worker.worker_id}
            assigs = []
            for assignment in worker.assignments:
                if assignment.is_answered():
                    assigs.append(assignment.to_dict())
            worker_obj['assignments'] = assigs
            workers.append(worker_obj)
        return workers

    def worker_has_demographics(self, worker_id) -> bool:
        if not self._check_worker_exists(worker_id):
            return False
        return self._get_worker(worker_id).age is not None

    def save_anwer(self, assign_id, answer, worker_id, demographics, extra=None):
        for a in self.assignments:
            if a.id == assign_id:
                a.answer = json.loads(answer)
                a.update_task(extra)
                self._update_jobs_assigned(a._task['condition'], a._task['images'])
                if a.worker_id != worker_id:
                    # update worker id!!
                    self._update_worker_id(a.worker_id, worker_id)
                    a.worker_id = worker_id
                for worker in self.workers:
                    if worker.worker_id == worker_id:
                        # update Assignments
                        worker.update_assignments(a)
                        if demographics:
                            # update Demographics
                            worker.update_demographics(json.loads(demographics))
                return True
        return False

    @real_task
    def get_task(self, worker_id, assign_id) -> dict:
        if self._is_new_assignment(assign_id):
            if not self._check_worker_exists(worker_id):
                self._set_up_worker(worker_id)
            if self._check_valid_worker(worker_id):
                # Get Task
                worker = self._get_worker(worker_id)
                task = worker.queue.get()

                # Make new Assignment
                a = Assignment(assign_id, worker_id=worker_id, task=task)
                self.assignments.append(a)
                return task
            else:
                return {"return": "all jobs done"}
        else:
            for assign in self.assignments:
                if assign.id == assign_id:
                    if assign.worker_id != worker_id:
                        # update worker id!!
                        self._update_worker_id(assign.worker_id, worker_id)
                        assign.worker_id = worker_id
                    return assign.task
            return {"ERROR": "Assignment ID not found"}

    @real_task
    def get_test_task(self, worker_id, assign_id, condition):
        if not self._check_worker_exists(worker_id):
            self._set_up_worker(worker_id, test=True)
        task = {"condition": condition, "images": np.random.choice(list(IMAGE_SETS.keys()))}
        a = Assignment(assign_id, worker_id=worker_id, task=task)
        self.assignments.append(a)
        return task

    def export_workers(self):
        new_worker = [vars(worker) for worker in self.workers]
        return new_worker

    def export_raw_data(self):
        return {"workers": self.export_workers(), "assignments": [a.to_dict() for a in self.assignments]}


if __name__ == '__main__':
    tasks = Tasks()
    flag = True
    while flag:
        wid = input("Worker ID: ")
        aid = input("Assgin ID: ")
        condition = input("condition: ")
        task = tasks.get_test_task(wid, aid, condition)
        assert(task['html'] == tasks.get_task(wid, aid)['html'])
        cont = input("continue? Y/N")
        if cont[0] == 'N':
            flag = False
