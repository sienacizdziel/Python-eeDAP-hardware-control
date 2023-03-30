''' dependencies ''' 
import cv2, queue
# import PySpin
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
from PIL import Image, ImageTk

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

# constants
IMAGE_HEIGHT = 240
IMAGE_WIDTH = 320
EXPOSURE_TIME = 500 # in microseconds
# PIXEL_FORMAT = PySpin.PixelFormat_RGB8

# cv2.videoCapture(PATH / ID)
# cap.read() for individually accessing frames
# read from .dapsi file for camera type
class Camera():
    def __init__(self):
        pass

class Grasshopper3Camera(Camera):
    def __init__(self, device=0):
        """ initialize video capture with device number """
        # discover camera
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        self.cam = cam_list.GetByIndex(device)
        # print(self.cam)
        # for i in range(10):
        #     print(cam_list.GetByIndex(i))
        # print(cam_list)

        # initialize camera parameters
        self.cam.Init()
        self.cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
        self.cam.UserSetLoad()

        print(self.cam)

        # set continuous acquisition for video streaming
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureMode.SetValue(PySpin.ExposureMode_Timed)
        self.cam.ExposureTime.SetValue(EXPOSURE_TIME)
        nodemap = self.cam.GetNodeMap()
        # frame_rate_auto_node = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionFrameRateAuto"))
        enable_rate_mode = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnabled"))
        enable_rate_mode.SetValue(False)
        # cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        # cam.AcquisitionFrameRateEnable.SetValue(False)

        # image format control
        # apply pixel format
        node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
        if PySpin.IsAvailable(node_pixel_format) and PySpin.IsWritable(node_pixel_format):
            # retrieve the desired entry node from the enumeration node and set as new value
            node_pixel_format_rgb8 = PySpin.CEnumEntryPtr(node_pixel_format.GetEntryByName("RGB8"))
            if PySpin.IsAvailable(node_pixel_format_rgb8) and PySpin.IsReadable(node_pixel_format_rgb8):
                pixel_format_rgb8 = node_pixel_format_rgb8.GetValue()
                node_pixel_format.SetIntValue(pixel_format_rgb8)
                print("Pixel format set to {}".format(node_pixel_format.GetCurrentEntry().GetSymbolic()))
            else:
                print("Pixel format not available...")

        # apply minimum to offset X
        node_offset_x = PySpin.CIntegerPtr(nodemap.GetNode("OffsetX"))
        if PySpin.IsAvailable(node_offset_x) and PySpin.IsWritable(node_offset_x):
            node_offset_x.SetValue(node_offset_x.GetMin())
            print("Offset X set to {}".format(node_offset_x.GetMin()))
        else:
            print("Offset X not available...")

        # apply minimum to offset Y
        node_offset_y = PySpin.CIntegerPtr(nodemap.GetNode("OffsetY"))
        if PySpin.IsAvailable(node_offset_y) and PySpin.IsWritable(node_offset_y):
            node_offset_y.SetValue(node_offset_y.GetMin())
            print("Offset Y set to {}".format(node_offset_y.GetMin()))
        else:
            print("Offset Y not available...")

        # apply maximum width
        node_width = PySpin.CIntegerPtr(nodemap.GetNode("Width"))
        if PySpin.IsAvailable(node_width) and PySpin.IsWritable(node_width):
            width_to_set = node_width.GetMax()
            node_width.SetValue(width_to_set)
            print("Width set to {}...".format(node_width.GetValue()))
        else:
            print("Width not available...")

        # apply maximum height
        node_height = PySpin.CIntegerPtr(nodemap.GetNode("Height"))
        if PySpin.IsAvailable(node_height) and PySpin.IsWritable(node_height):
            height_to_set = node_height.GetMax()
            node_height.SetValue(height_to_set)
            print("Height set to {}...".format(node_height.GetValue()))
        else:
            print("Height not available...")
        

        # get frame rate and other parameters
        self.seconds = 10
        self.frame_rate = 163 # need to pull this somehow
        print(self.frame_rate)
        self.num_images = round(self.frame_rate * self.seconds) # calculation based on number of frames per second
        # print("frame rate: " + self.frame_rate)

        # initialize tkinter for video output
        self.window = tk.Tk()
        self.window.title("camera view")
        width = str(IMAGE_WIDTH + 25) # why 25?
        height = str(IMAGE_HEIGHT + 35)
        self.window.geometry(width + 'x' + height)
        textlbl = tk.Label(self.window, text="elapsed time: ")
        textlbl.grid(column=0, row=0)
        self.imglabel = tk.Label(self.window)
        self.imglabel.place(x=10, y=20)
        self.window.update()

        # self.cam.BeginAcquisition()
        # print("here!")
        self.camera_preview()
        # self.window.mainloop()

        # set up a thread to accelerate saving
          
          # image.Save('test.jpg') 
        # self.cam.EndAcquisition()
        # self.cam.DeInit()
        # print(cam_list)

    def camera_preview(self):
        """ display preview of camera """
        """ references camera_open.m from eeDAP """
        print("here??")
        # cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
        self.cam.BeginAcquisition()
        # width = image_primary.GetWidth()
        # height = image_primary.GetHeight()
        # print("width: " + str(width) + ", height: " + str(height))

        # create a queue to store images while asynchronously written to disk
        image_queue = queue.Queue()

        # loop through images in video
        print("here")
        print(self.num_images)
        for i in range(self.num_images):
          frame = self.cam.GetNextImage()
          # frame = frame.Convert(self.pixel_format)
          # print(frame.GetWidth())
          # node_pixel_format = PySpin.CEnumerationPtr
          # convert PySpin ImagePtr into numpy array
          # frame = frame.Convert(self.pixel_format, PySpin.HQ_LINEAR)
          image = np.array(frame.GetData(), dtype="uint8").reshape(frame.GetHeight(), frame.GetWidth())
          # image = np.array(frame.GetData(), dtype="uint8")
          image_queue.put(image)

          # update screen every 10 frames
          if i % 10 == 0:
              I = ImageTk.PhotoImage(Image.fromarray(image))
              self.imglabel.configure(image=I)
              self.imglabel.image = I
              self.window.update()

          # release frame from camera buffer
          frame.Release()

        # while self.cap.isOpened():
        #     ret, frame = self.cap.read()
        #     print(ret, frame)
        #     if not ret:
        #         print("failed to read frame")
        #         break
        #     else: 
        #         ret, buffer = cv2.imencode('.jpg', frame)
        #         frame = buffer.tobytes()
        #         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    def take_image(self):
        """ capture an image frame from video """
        """ references camera_take_image.m from eeDAP """
        pass
        
    def destroy(self):
        """ destroys all instances of camera, in order to safely end a video """
        pass

