''' contains helper functions for tasks '''
import random

SLIDE_OFFSET = 0

class Task: 
    # class for tasks provided in dapsi file (contains ROIs)
    def __init__(self, list):
        self._parse_input(list.split(','))

    def _parse_input(self, list):
        if len(list) < 8:
            print("task incorrectly formatted")
            return
        self.name, self.id, self.order, self.slot = list[0:4] # task id info
        self.q_text = list[8] # question text
        self.x, self.y, self.w, self.h = [int(val) for val in list[4:8]] # roi coordinates

    def _get_slide_number(self):
        try:
            parsed_id = self.id.split('_')
            return parsed_id[0].split('-')[::-1][0]
        except:
            print('Could not parse slide ID: ' + self.id + '. Continuing with successfully parsed IDs.')
            return None
            

def randomize_tasks(tasks):
    # input: list of tasks from session
    # output: randomized list of tasks for experiment
    tasks_copy = tasks.copy()
    random.shuffle(tasks_copy)
    return tasks_copy

def get_all_slide_numbers(tasks):
    # input: list of tasks from session
    # output: sorted list of the 4 possible slide numbers
    slide_nums = []
    nums_seen = []
    try:
      for task in tasks:
          full_num = task._get_slide_number()
          if not full_num:
              continue
          print(full_num)
          num = full_num[:len(full_num) - 1]
          print(num)
          if full_num not in nums_seen:
              slide_nums.append((int(num), full_num))
              nums_seen.append(full_num)
      print(slide_nums)
      slide_nums = sorted(slide_nums, key=lambda x: x[0])
      return [x[1] for x in slide_nums]
    except:
        print("Slide numbers incorrectly formatted: should be integer + letter, for example 70b. Received " + task._get_slide_number())

def visit_task(stage, task, slide_offset):
    # input: initialized prior stage, task to visit, x coordinate slide offset
    # moves the stage to the desired task based off the offsets
    stage.move_to({'x': task.x + slide_offset, 'y': task.y})
