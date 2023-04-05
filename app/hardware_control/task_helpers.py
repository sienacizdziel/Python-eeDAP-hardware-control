''' contains helper functions for tasks '''
import random

class Task: 
    # class for tasks provided in dapsi file (contains ROIs)
    def __init__(self, list):
        self._parse_input(list.split(','))

    def _parse_input(self, list):
        self.name, self.id, self.order, self.slot = list[0:4] # task id info
        self.q_text = list[8] # question text
        self.x, self.y, self.w, self.h = [int(val) for val in list[4:8]] # roi coordinates

def randomize_tasks(tasks):
    # input: list of tasks from session
    # output: randomized list of tasks for experiment
    tasks_copy = tasks.copy()
    random.shuffle(tasks_copy)
    return tasks_copy