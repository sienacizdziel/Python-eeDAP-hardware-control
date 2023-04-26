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

# ptgrey camera with PySpin tutorial: https://github.com/nimble00/PTGREY-cameras-with-python 

''' additional considerations '''
# live view (rgb)
# generalizability to all 3 eeDAP-supported cameras
    # digital interface is USB for Blenman lab camera but IEEE-1394b for others
# eyepiece offset

# constants
IMAGE_HEIGHT = 240
IMAGE_WIDTH = 320
WIDTH_OFFSET = round((720 - IMAGE_WIDTH) / 2)
HEIGHT_OFFSET = round((540 - IMAGE_HEIGHT) / 2)
EXPOSURE_TIME = 500 # in microseconds
PIXEL_FORMAT = PySpin.PixelFormat_RGB8

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

        
        nodemap = self.cam.GetNodeMap()
        enable_rate_mode = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnabled"))
        enable_rate_mode.SetValue(False)

        # potential options for offsetting x and y coordinates
        # self.cam.OffsetX.SetValue(WIDTH_OFFSET)
        # self.cam.OffsetY.SetValue(HEIGHT_OFFSET)

        # image format control
        # apply pixel format
        # node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
        # if PySpin.IsAvailable(node_pixel_format) and PySpin.IsWritable(node_pixel_format):
        #     # retrieve the desired entry node from the enumeration node and set as new value
        #     node_pixel_format_rgb8 = PySpin.CEnumEntryPtr(node_pixel_format.GetEntryByName("BayerRG8"))
        #     if PySpin.IsAvailable(node_pixel_format_rgb8) and PySpin.IsReadable(node_pixel_format_rgb8):
        #         pixel_format_rgb8 = node_pixel_format_rgb8.GetValue()
        #         node_pixel_format.SetIntValue(pixel_format_rgb8)
        #         print("Pixel format set to {}".format(node_pixel_format.GetCurrentEntry().GetSymbolic()))
        #     else:
        #         print("Pixel format not available...")
        

        # get frame rate and other parameters
        self.seconds = 10
        self.frame_rate = 75 # found on the spinnaker site for model: GS3-U3-51S5C-C
        self.num_images = round(self.frame_rate * self.seconds) # calculation based on number of frames per second

        # initialize tkinter for video output
        self.window = tk.Tk()
        self.window.title("camera view")
        width = str(IMAGE_WIDTH + 25) 
        height = str(IMAGE_HEIGHT + 35)
        self.window.geometry(width + 'x' + height)
        self.imglabel = tk.Label(self.window)
        self.imglabel.place(x=10, y=20)
        self.window.update()

        self.camera_preview()

        # set up a thread to accelerate saving
          
          # image.Save('test.jpg') 
        # self.cam.EndAcquisition()
        # self.cam.DeInit()
        # print(cam_list)

    def camera_preview(self):
        """ display preview of camera """
        """ references camera_open.m from eeDAP """
        # cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
        self.cam.BeginAcquisition()
        # width = image_primary.GetWidth()
        # height = image_primary.GetHeight()
        # print("width: " + str(width) + ", height: " + str(height))

        # create a queue to store images while asynchronously written to disk
        # image_queue = queue.Queue()
        processor = PySpin.ImageProcessor()
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

        # loop through images in video
        print("here")
        print(self.num_images)
        i = 0
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
              print('Camera grabbed image %d, width = %d, height = %d' % (i, width, height))

              # convert image to mono 8
              # image = processor.Convert(frame, PySpin.PixelFormat_BayerBG8)

          # frame = frame.Convert(PySpin.PixelFormat_BayerBG8)
          # print(frame.GetWidth())
          # node_pixel_format = PySpin.CEnumerationPtr
          # convert PySpin ImagePtr into numpy array
          processed_frame = processor.Convert(frame, PySpin.PixelFormat_RGB8)
          # image = frame.GetData()
          image = np.array(processed_frame.GetData(), dtype="uint8").reshape(height, width, 3)
          # image = np.array(frame.GetData(), dtype="uint8")
          # image = np.array(frame.GetData(), dtype="uint8")
          # image_queue.put(image)

          # update screen every x frames
          if i % 6 == 0:
              # rgb_image = Image.fromarray(image)
              # buf = BytesIO()
              # rgb_image.save(buf, 'JPEG')
              # frame = buf.getbuffer()
              # yield(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
              I = ImageTk.PhotoImage((Image.fromarray(image)).resize((width // 2, height // 2)))
              self.imglabel.configure(image=I)
              self.imglabel.image = I
              self.window.update()

              # buffer = cv2.imencode('.jpg', image)
              # image = buffer.tobytes()
              # yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

          # release frame from camera buffer
          frame.Release()
          i = (i + 1) % 100


    def take_image(self):
        """ capture an image frame from video """
        """ references camera_take_image.m from eeDAP """
        pass
        
    def destroy(self):
        """ destroys all instances of camera, in order to safely end a video """
        pass
    