from xmlrpc.client import Boolean
import serial
import threading

# ser = serial.Serial()
# print(ser.name)

# check into baudrate (19200?), and timeout

# this version isn't open
# ser.port = 'COM4'
# print(ser)

# this one is still not open
# ser2 = serial.Serial()
# ser2.port = 'COM4'
# print(ser2)

# this opens the port COM4, plus names this object COM4
# ser = serial.Serial('COM4') # default baudrate = 9600
# print(ser)

# # look more into the following for error checking
# # if ser.isopen():
# #     print("this test passed")
# #     pass

# # and close the port
# ser.close()
# print(ser)

# # open it again
# ser.open()
# print(ser)

class _PriorConnection:
    """Wraps serial connection with a reentrant lock
    
    This class wraps serial.Serial, for the stage's connection via Serial Port
    
    On Dr. Blenman's computer, use port COM4"""
    def __init__(self, port: str) -> None: #, baudrate: int, timeout: float) -> None:
        self._serial = serial.Serial(
            port=port,
            baudrate= 9600, # based on eeDAP source code
            timeout=3, # also based on eeDAP source code
            bytesize=serial.EIGHTBITS, # --> TODO: because not included in eeDAP source code
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )
        self._lock = threading.RLock()
        with self._lock:
            # The command / does nothing other than getting a response
            # from all devices in the chain.  This seems to be the
            # most innocent command we can use.
            self._serial.write(b"/\n")
            lines = self._serial.readlines()
        if not all([l.startswith(b"@") for l in lines]):
            raise RuntimeError(
                "'%s' does not respond like a Prior device" % port
            )

    @property
    def lock(self) -> threading.RLock:
        return self._lock

    def write(self, data: bytes) -> int:
        with self.lock:
            return self._serial.write(data)

    def readline(self, size: int = -1) -> bytes:
        with self.lock:
            return self._serial.readline(size)

    def close(self) -> None:
        return self._serial.close()

# returns the number of bytes written to the specified serial port
# otherwise, on error, returns -1
def send_com_prior_stage(serial_port:_PriorConnection, command:str) -> int:
    # for each char in the command, send to the stage
    # for i in command:
    #     serial_port.write(i)
    try:
        # send command string as bytes
        # serial_port.write(bytes(command, encoding='utf-8'))
        # command_b = bytes(command, encoding='utf-8')
        command_new = command + "\r\n"
        # print(command_new)
        command_b = bytes(command_new.encode())
        # for i in range(len(command_b)):
        #     print(bytes(command[i], encoding='utf-8'))
        #     serial_port.write(bytes(command[i], encoding='utf-8'))
            # serial_port.write(command_b[i])

        # must be encoded to bytes (unicode strings not supported)
        # prints number of bytes written
        # print(serial_port.write(command_b))
        serial_port.write(command_b)

        # send the termination char
        # serial_port.write(bytes(13, encoding='utf-8'))

        serial_answer = serial_port.readline()

        # print(serial_answer)
        # print(serial_answer.decode('utf-8'))
        print(serial_answer.decode("ASCII"))

        # error messages from stage
        # TODO compare to byte strings?
        if serial_answer == b'E,1\r':
            print("No Prior Stage connected")
            serial_answer = -1
        if serial_answer == b'E,2\r':
            print("Prior Stage not idle")
            serial_answer = -1
        if serial_answer == b'E,3\r':
            print("No Prior driver")
            serial_answer = -1 
        if serial_answer == b'E,4\r':
            print("String parsing error")
            serial_answer = -1
        if serial_answer == b'E,5\r':
            print("Command for Prior Stage not found")
            serial_answer = -1
        if serial_answer == b'E,8\r':
            print("Value out of range")
            serial_answer = -1
    except Exception as e:
        print("an exception occured: " + str(e))
        serial_answer = -1


