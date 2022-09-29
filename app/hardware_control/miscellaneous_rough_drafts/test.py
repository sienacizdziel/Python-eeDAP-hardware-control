from com_connect_tester import _PriorConnection
from com_connect_tester import send_com_prior_stage
import time

ser = _PriorConnection("COM4")
print(ser)
print(ser._serial)

# send_com_prior_stage(ser, 'hiiii what')
# send_com_prior_stage(ser, 'G -100000,-100000 CR')
# send_com_prior_stage(ser, 'Z')
# send_com_prior_stage(ser, 'G 50,50')
# send_com_prior_stage(ser, 'G -50,-50') 
# send_com_prior_stage(ser, 'PS')
# send_com_prior_stage(ser, 'where x y')
# send_com_prior_stage(ser, '')
# send_com_prior_stage(ser, 'COMP 0\r\n')
send_com_prior_stage(ser, "COMP 0")
time.sleep(5)
send_com_prior_stage(ser, 'G -100000,-100000')

# time.sleep(5)

# to set origin
# send_com_prior_stage(ser, "COMP 0")
# time.sleep(5)
# send_com_prior_stage(ser, 'G -100000,-100000')
time.sleep(10)

# TODO: checking if prior is busy
send_com_prior_stage(ser, "Z")
time.sleep(5)
send_com_prior_stage(ser, "G 5000 5000")
time.sleep(10)
send_com_prior_stage(ser, "G -5000 -5000")
time.sleep(10)


ser.close()


# print to make sure you are connecting to the right COM for the stage
import serial.tools.list_ports
my_ports=[tuple(p) for p in list(serial.tools.list_ports.comports())]
print(my_ports)