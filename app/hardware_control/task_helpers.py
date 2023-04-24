''' contains helper functions for tasks '''
import random

class Task:
    """ 
    class for tasks provided in the uploaded dapsi file
    input is a comma-separated string that contains: 
        task name (example: HTT_TILS_20x),
        task ID (example: HTT-TILS-001-81B_left_44042_top_12737),
        task order,
        slot, 
        ROI_X (x coordinate of ROI),
        ROI_Y (y coordinate of ROI), 
        ROI_W (width of ROI), 
        ROI_H (height of ROI), 
        Q_text
    """
    def __init__(self, list):
        # parse the input string, split by commas
        self._parse_input(list.split(','))

    def _parse_input(self, list):
        # parses through a list for task attributes
        if len(list) < 8:
            print("Task is incorrectly formatted.")
            return
        self.name, self.id, self.order, self.slot = list[0:4] # task id info
        self.q_text = list[8] # question text
        self.x, self.y, self.w, self.h = [int(val) for val in list[4:8]] # roi coordinates

    def _get_slide_number(self):
        # parses the task id for its slide number
        # note that a task id is in a format like: HTT-TILS-001-81B_left_44042_top_12737
        # in the above case, 81B is the slide number
        try:
            parsed_id = self.id.split('_')
            return parsed_id[0].split('-')[::-1][0]
        except:
            print('Could not parse slide ID: ' + self.id + '. Continuing with successfully parsed IDs.')
            return None
            

def randomize_tasks(tasks):
    """ 
    randomizes a list of tasks for experiment
    input: list of Task classes from session
    output: randomized list of Task classes for experiment
    """
    tasks_copy = tasks.copy()
    random.shuffle(tasks_copy)
    return tasks_copy

def get_all_slide_numbers(tasks):
    """ 
    returns a list of slide numbers (example: [81B, 82B, 83B, 84B])
    input: list of Task classes from session
    output: sorted list of the possible slide numbers existing in the tasks (usually, 4 slides)
    # sorted by the integer value in the slide number
    """
    slide_nums = []
    nums_seen = []

    try:
      # loop through each possible task
      for task in tasks:
          full_num = task._get_slide_number()
          if not full_num:
              continue
          num = full_num[:len(full_num) - 1]
          # append each slide number if not already seen
          if full_num not in nums_seen:
              slide_nums.append((int(num), full_num))
              nums_seen.append(full_num)

      # sort through slide numbers
      slide_nums = sorted(slide_nums, key=lambda x: x[0])
      return [x[1] for x in slide_nums]
    except:
        print("Slide numbers incorrectly formatted: should be integer + letter, for example 70b. Received " + task._get_slide_number())

def visit_task(stage, task, slide_offset=0):
    """ 
    moves the stage to the provided ROI task coordinates, offset by the provided offset value
    input: 
        - stage = PriorStage class
        - task = Task class to be visited
        - slide_offset = optional param for the x-coord offset of the slide 
    """
    stage.move_to({'x': task.x + slide_offset, 'y': task.y})
