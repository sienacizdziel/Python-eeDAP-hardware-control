import cv2, queue
import PySpin
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from abc import ABCMeta, abstractmethod

""" 
Creates an abstract base parent class for cameras & implements the camera 
class for the Grasshopper3 camera using PySpin (a Python wrapper for the 
FLIR Spinnaker SDK API library, which supports FLIR Point Grey cameras)
"""

# constants
IMAGE_HEIGHT = 240
IMAGE_WIDTH = 320
WIDTH_OFFSET = round((720 - IMAGE_WIDTH) / 2)
HEIGHT_OFFSET = round((540 - IMAGE_HEIGHT) / 2)
EXPOSURE_TIME = 500 # in microseconds
FRAME_UPDATE = 6 # number of frames that go by before a new one is displayed


class Camera(metaclass=ABCMeta):
    """ parent class for cameras"""

    def __init__(self):
        pass

    @abstractmethod
    def camera_preview(self):
        """ show camera preview """
        raise NotImplementedError()


class Grasshopper3Camera(Camera):
    """ camera class for the Grasshopper3 FLIR camera """
    def __init__(self, device=0):
        super().__init__()

        """ initialize video capture with device number, which defaults to 0 """
        # discover camera
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        self.cam = cam_list.GetByIndex(device)

        # to view the first 10 cameras accessible via the system, uncomment the code below
        # print(cam_list)
        # for i in range(10):
        #     print(cam_list.GetByIndex(i))

        # initialize camera parameters
        self.cam.Init()
        self.cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
        self.cam.UserSetLoad()

        # set continuous acquisition and exposure values for continuous streaming
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureMode.SetValue(PySpin.ExposureMode_Timed)
        self.cam.ExposureTime.SetValue(EXPOSURE_TIME)

        # get node map for changing high-level features
        nodemap = self.cam.GetNodeMap()
        enable_rate_mode = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnabled"))
        enable_rate_mode.SetValue(False)

        # potential options for offsetting x and y coordinates
        # self.cam.OffsetX.SetValue(WIDTH_OFFSET)
        # self.cam.OffsetY.SetValue(HEIGHT_OFFSET)

        # additional parameters
        self.frame_rate = 75 # found on the spinnaker site for model: GS3-U3-51S5C-C

        # initialize tkinter for video output
        self.window = tk.Tk()
        self.window.title("camera view")
        width = str(IMAGE_WIDTH + 25) 
        height = str(IMAGE_HEIGHT + 35)
        self.window.geometry(width + 'x' + height)
        self.imglabel = tk.Label(self.window)
        self.imglabel.place(x=10, y=20)
        self.window.update()

        # preview camera
        self.camera_preview()


    def camera_preview(self):
        """ display preview of camera """
        """ references camera_open.m from eeDAP """

        # begin acquiring images
        self.cam.BeginAcquisition()

        # create ImageProcessor, a post-processing class for converting a source image's pixel format
        processor = PySpin.ImageProcessor()
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

        i = 0
        # loop through images in video
        while True:
          # retrieve next image
          frame = self.cam.GetNextImage()

          # ensure image is complete
          if frame.IsIncomplete():
              print('Image incomplete with image status %d ... \n' % frame.GetImageStatus())
              continue
          else:
              # print image information
              width = frame.GetWidth()
              height = frame.GetHeight()
              print('Camera grabbed image width = %d, height = %d' % (width, height))

          # convert frame to RGB
          processed_frame = processor.Convert(frame, PySpin.PixelFormat_RGB8)

          # convert PySpin ImagePtr into numpy array
          image = np.array(processed_frame.GetData(), dtype="uint8").reshape(height, width, 3)

          # update tkinter display every x frames
          if i % FRAME_UPDATE == 0:
              
              # create & update the tkinter image
              I = ImageTk.PhotoImage((Image.fromarray(image)).resize((width // 2, height // 2)))
              self.imglabel.configure(image=I)
              self.imglabel.image = I
              self.window.update()

          # release frame from camera buffer
          frame.Release()
          i = (i + 1) % 100


    def take_image(self):
        """ capture an image frame from video """
        """ references camera_take_image.m from eeDAP """
        pass
 

    def destroy(self):
        """ destroys all instances of camera, in order to safely end a video """
        self.cam.EndAcquisition()
        self.cam.DeInit()
