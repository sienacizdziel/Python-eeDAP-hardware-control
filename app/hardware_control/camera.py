import cv2 
from matplotlib import pyplot as plt
import PySpin # spinnaker is a proprietary library that supports FLIR pointgrey cameras

# opencv & usb tutorial: https://www.youtube.com/watch?v=FygLqV15TxQ 
# flask & opencv video tutorial: https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00 

# considerations:
# live view (rgb)
# generalizability to all 3 eeDAP-supported cameras
    # digital interface is USB for Blenman lab camera but IEEE-1394b for others
# eyepiece offset

# cv2.videoCapture(PATH / ID)
# cap.read() for individually accessing frames
# read from .dapsi file for camera type
class Camera():
    def __init__(self):
        pass

class Grasshopper3Camera(Camera):
    def __init__(self, device=0):
        """ initialize video capture with device number """
        # for i in range(10): 
        #   self.cap = cv2.VideoCapture(i)
        #   print(str(i) + ": " + str(self.cap.read()[0]))
        #   self.cap.release()
        # self.cap = cv2.VideoCapture(1)
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        print(cam_list)

    def camera_preview(self):
        """ display preview of camera """
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            print(ret, frame)
            if not ret:
                print("failed to read frame")
                break
            else: 
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def take_image(self):
        """  """
        ret, frame = self.cap.read()
        cv2.imwrite('image.jpg', frame) # photo name

        # cap.release() releases a webcam device

    # abstract methods:
    # open camera (camera_open.m)
    # take image (camera_take_image.m)