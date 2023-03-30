# Usage: python move_stage_tester.py
# Python version = Python 3.8.10

from prior_stage.proscan import PriorStage
from os import sys
from serial import SerialException

print("running move stage tester")

# initialize communication with Prior ProScan III
# input the appropriate COM port
try:
  p = PriorStage("COM4")
except SerialException as e:
  print(e)
  sys.exit(0)

# testing: move to provided coordinates
# coordinate provided in JSON format
# if the stage is already at those coordinates, it will not move
p.move_to({'x': -100000, 'y': -100000})
p.move_to({'x': 100000, 'y': 100000})

# close serial port communication
p.close()