from com_connect_tester import _PriorConnection
from com_connect_tester import send_com_prior_stage

ser = _PriorConnection("COM4")
print(ser)
print(ser._serial)

send_com_prior_stage(ser, 'hiiii what')
# send_com_prior_stage(ser, 'G -100000,-100000')
# send_com_prior_stage(ser, 'Z')
# send_com_prior_stage(ser, 'G 50,50')
# send_com_prior_stage(ser, 'G -50,-50') 
send_com_prior_stage(ser, 'PS')
send_com_prior_stage(ser, 'where x y')
send_com_prior_stage(ser, '')


# print to make sure you are connecting to the right COM for the stage
import serial.tools.list_ports
my_ports=[tuple(p) for p in list(serial.tools.list_ports.comports())]
print(my_ports)