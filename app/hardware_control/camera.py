''' dependencies ''' 
import cv2, PySpin, queue
import numpy as np
from matplotlib import pyplot as plt

# PySpin is a python wrapper for the Spinnaker library
# Spinnaker SDK is FLIR's next generation GenlCam3 API library for cameras
# supports FLIR pointgrey cameras

''' tutorials '''
# opencv & usb tutorial (not used): https://www.youtube.com/watch?v=FygLqV15TxQ 
# flask & opencv video tutorial: https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00 
# ptgrey camera with PySpin tutorial: https://github.com/nimble00/PTGREY-cameras-with-python 

''' additional considerations '''
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
        # initialize specified camera
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        self.cam = cam_list.GetByIndex(device)
        self.cam.Init()

        # set continuous acquisition for video streaming
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        # cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        # cam.AcquisitionFrameRateEnable.SetValue(False)

        # get framerate and other parameters
        self.frame_rate = self.cam.AcquisitionResultingFrameRate()

        # cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
        self.cam.BeginAcquisition()
        frame = self.cam.GetNextImage()
        # width = image_primary.GetWidth()
        # height = image_primary.GetHeight()
        # print("width: " + str(width) + ", height: " + str(height))

        # convert PySpin ImagePtr into numpy array
        image = np.array(frame.GetData(), dtype="uint8").reshape(frame.getHeight(), frame.getWidth())
        image.Save('test.jpg') 
        self.cam.EndAcquisition()
        self.cam.DeInit()
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
        """ capture an image frame from video """
        

    # abstract methods:
    # open camera (camera_open.m)
    # take image (camera_take_image.m)
