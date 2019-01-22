import numpy as np
import cv2 as cv
import sys
from video import create_capture
import imutils
import argparse
import datetime
import time
from time import sleep

TMPFILENAME = "tmp.png"

class capture:
    def __init__(self):
        self.firstFrame = None
        self.camera     = None

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

        self.firstFrame = self.resizeConvertBlur(frame)
        self.close()
        return 0

    def reinit(self):
        if(self.camera):
            self.camera.release()
        self.camera     = None
        self.firstFrame = None
        return self.init()

    def open(self):
        self.camera = create_capture(0)
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

    def fetch(self):
        text = "Empty"
        ok, frame = self.open()
        if not ok:
            return -1, "no_image", 0, 0

        self.close()

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if frame is None:
            return -1, "no_frame", 0, 0

        gray = self.resizeConvertBlur(frame)

        frameDelta = cv.absdiff(self.firstFrame, gray)
        thresh = cv.threshold(frameDelta, 25, 255, cv.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv.dilate(thresh, None, iterations=2)
        cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
	                       cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

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
        cv.putText(frame, "Room Status: {}".format(text), (10, 20),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv.putText(frame, dt, (10, frame.shape[0] - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        cv.imwrite(TMPFILENAME, frame, [cv.IMWRITE_PNG_COMPRESSION, 5])
        return 0, TMPFILENAME, len(cnts), timestamp
