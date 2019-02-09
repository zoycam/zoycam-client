import numpy as np
import cv2 as cv
from video import create_capture
import imutils
import argparse
import datetime
import time
import os, sys
from time import sleep

class capture:
    def __init__(self):
        self.firstFrame = None
        self.camera     = None
        self.node       = 0
        self.processing = "opencv"
        self.detector   = None
        self.execution_path = None

    @staticmethod
    def resizeConvertBlur(frame):
        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        return cv.GaussianBlur(gray, (21, 21), 0)

    def init(self):
        ok, frame = self.open()
        if not ok:
            return -1

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if frame is None:
            return -1

        self.firstFrame = capture.resizeConvertBlur(frame)
        self.close()
        return 0

    def setparams(self, params):
        self.node       = int(params["node"])
        self.processing = params["processing"]

        if(self.processing == "imageai"):
            from imageai.Detection import ObjectDetection
            self.execution_path = os.getcwd()
            self.detector = ObjectDetection()
            self.detector.setModelTypeAsYOLOv3()
            self.detector.setModelPath(os.path.join(self.execution_path , "yolo.h5"))
            self.detector.loadModel()

    def reinit(self):
        if(self.camera):
            self.camera.release()
        self.camera     = None
        self.firstFrame = None
        return self.init()

    def open(self):
        self.camera = create_capture(self.node)
        self.camera.set(cv.CAP_PROP_BUFFERSIZE, 1)
        ok, frame = self.camera.read()
        if not ok:
            print('Failed to read video')
            return 0, None
        return 1, frame

    def close(self):
        if(self.camera):
            self.camera.release()
        self.camera = None

    def genfname(self):
        return "tmp%d.png" % self.node

    def imageai(self, frame):
        filename = self.genfname()
        cv.imwrite(self.genfname(), frame, [cv.IMWRITE_PNG_COMPRESSION, 5])
        detections = self.detector.detectObjectsFromImage(input_image=os.path.join(self.execution_path, filename), output_image_path=os.path.join(self.execution_path , filename), minimum_percentage_probability=30)
        return 0, filename, len(detections), time.time()

    def fetch(self):
        ok, frame = self.open()
        if not ok:
            return -1, "no_image", 0, 0

        self.close()
        frame = imutils.resize(frame, width=300)

        if(self.processing == "imageai"): return self.imageai(frame)

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if frame is None:
            return -1, "no_frame", 0, 0

        gray = capture.resizeConvertBlur(frame)

        frameDelta = cv.absdiff(self.firstFrame, gray)
        thresh = cv.threshold(frameDelta, 25, 255, cv.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv.dilate(thresh, None, iterations=2)
        cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
	                       cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        text = "Empty"
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv.contourArea(c) < 500:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv.boundingRect(c)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

        # draw the text and timestamp on the frame
        dt = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
        timestamp = time.time()
        cv.putText(frame, "Status: {}".format(text), (10, 20),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv.putText(frame, dt, (10, frame.shape[0] - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        filename = self.genfname()
        cv.imwrite(filename, frame, [cv.IMWRITE_PNG_COMPRESSION, 5])
        return 0, filename, len(cnts), timestamp
