import cv2 
from matplotlib import pyplot as plt

# opencv & usb tutorial: https://www.youtube.com/watch?v=FygLqV15TxQ 
# flask & opencv video tutorial: https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00 

# considerations:
# live view (rgb)
# generalizability to all 3 eeDAP-supported cameras
    # digital interface is USB for Blenman lab camera but IEEE-1394b for others
# eyepiece offset
# read from .dapsi file for camera type

# methods from eedap matlab code:
    # open camera (camera_open.m)
    # take image (camera_take_image.m)

# abstract class for camera
class Camera():
    def __init__(self):
        pass

# blenman lab camera type
class Grasshopper3Camera(Camera):
    def __init__(self, device=0):
        """ initialize video capture with device number """
        self.cap = cv2.VideoCapture(device)

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