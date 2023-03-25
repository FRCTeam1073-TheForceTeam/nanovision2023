#!/usr/bin/env python3

import numpy as np
import cv2
import math
import apriltag
from networktables import NetworkTables
import sys
import time
import os

if len(sys.argv)<5:
    print("Server {videoDevice} {NetworkTable} {DestinationIP} {DestinationPort}")
    exit()


captureDevice=sys.argv[1]
networkTable=sys.argv[2]
destinationIP=sys.argv[3]
destinationPort=sys.argv[4]

#set the camera controls
cameraControlCommand="v4l2-ctl -d %s --set-ctrl exposure_auto=1,exposure_absolute=150,white_balance_temperature_auto=0,white_balance_temperature=4500,gain=6"%captureDevice 
if os.system(cameraControlCommand) != 0:
    print("error setting Camera controls")

# Capture Video and set resolution from gstreamer pipeline
#capture_pipeline = "nvarguscamerasrc do-timestamp=true ! video/x-raw(memory:NVMM),format=(string)NV12,width=(int)1920,height=(int)1080,framerate=30/1 ! nvvidconv flip-method=0 ! video/x-raw,width=(int)640,height=(int)360,format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink emit-signals=True drop=true"#capture_pipeline = "nvarguscamerasrc do-timestamp=true ! video/x-raw(memory:NVMM),format=(string)NV12,width=(int)1920,height=(int)1080,framerate=30/1 ! nvvidconv flip-method=0 ! video/x-raw,width=(int)640,height=(int)360,format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink emit-signals=True drop=true"
capture_pipeline = "v4l2src device=%s ! video/x-raw,format=(string)UYVY,width=(int)1280,height=(int)720,framerate=60/1 ! videorate max-rate=30 ! videoscale ! video/x-raw,width=(int)640,height=(int)360 ! videoconvert ! video/x-raw,format=(string)BGR ! appsink emit-signals=True drop=true"%(captureDevice)
capture = cv2.VideoCapture(capture_pipeline)

# Video output streaming to gstreamer pipeline
output_pipeline = "appsrc ! videoconvert ! video/x-raw,format=(string)NV12 ! omxh264enc control-rate=2 bitrate=400000 profile=1 preset-level=1 ! video/x-h264, framerate=30/1, stream-format=(string)byte-stream ! h264parse ! rtph264pay config-interval=1 mtu=1000 ! udpsink host=%s port=%s"%(destinationIP, destinationPort)

output = cv2.VideoWriter(output_pipeline, cv2.CAP_GSTREAMER, 30, (640, 360))

print("OpenCV Version " + cv2.__version__)
print("CUDA %d"%(cv2.cuda.getCudaEnabledDeviceCount()))

if capture.isOpened():
    print("Capture input pipeline created successfully...")
else:
    print("Capture input pipeline creation failed!")

if output.isOpened():
    print("Video output pipeline created successfully...")
else:
    print("Video output pipeline creation failed!")

detectorOptions = apriltag.DetectorOptions(families="tag16h5")
detector = apriltag.Detector(detectorOptions)

networkTableIP = "10.10.73.2"

# networktables.startClientTeam(1073)
# init network tables and "points" it at your robot [via robotpy]

NetworkTables.initialize(server=networkTableIP)

# Create network table with given table name:
table = NetworkTables.getTable(networkTable)

def tagDetection(image, frame):
    tags = detector.detect(image);

    if len(tags) > 0:
        print("{} total tags detected".format(len(tags)))

    tagOutput = []

    # Draw target lines over the video.
    for tag in tags:
        (ptA, ptB, ptC, ptD) = tag.corners;
        height = abs(ptA[1] - ptC[1])
        width =  abs(ptA[0] - ptC[0])
        if height > 10 and width > 10:
            aspectratio = width/height
            if aspectratio > 0.3 and aspectratio < 3.0:
                ptB = (int(ptB[0]), int(ptB[1]))
                ptC = (int(ptC[0]), int(ptC[1]))
                ptD = (int(ptD[0]), int(ptD[1]))
                ptA = (int(ptA[0]), int(ptA[1]))

                cv2.line(frame, ptA, ptB, (0,0,250), 2)
                cv2.line(frame, ptB, ptC, (0,0,250), 2)
                cv2.line(frame, ptC, ptD, (0,0,250), 2)
                cv2.line(frame, ptD, ptA, (0,0,250), 2)

                (cX, cY) = (int(tag.center[0]), int(tag.center[1]))
                cv2.circle(frame, (cX,cY), 5, (0,0,255), -1)

                tagId = "{}".format(tag.tag_id)

                cv2.putText(frame, tagId, (ptA[0], ptA[1]-15),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

                tagOutput+= [tag.tag_id, tag.hamming, tag.goodness, tag.decision_margin,
                tag.homography[0][0], tag.homography[0][1], tag.homography[0][2],
                tag.homography[1][0], tag.homography[1][1], tag.homography[1][2],
                tag.homography[2][0], tag.homography[2][1], tag.homography[2][2],
                tag.center[0], tag.center[1],
                tag.corners[0][0], tag.corners[0][1],
                tag.corners[3][0], tag.corners[3][1],
                tag.corners[2][0], tag.corners[2][1],
                tag.corners[1][0], tag.corners[1][1]]


   #connects with Network Tables, grabs number of tags found
    table.putNumberArray("Tags1", tagOutput)



# Cube Detector
cubeLower = (5,100,70)
cubeUpper = (235,220,110)

#image is the thing we are prossesing, frame is the thing we are drawing output on
def cubeDetection(image, frame):
    mask = cv2.inRange(image, cubeLower, cubeUpper)
    mask = cv2.erode(mask, None, iterations = 2)
    mask = cv2.dilate(mask, None, iterations = 2)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  #  cv2.drawContours(frame, contours, -3, (0,255,0), 2)
    cubes = []
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        area = w*h
        if area > 300 and w/h < 2.0 and w/h > 0.5:
            cubes += [x,y,w,h]
            cv2.rectangle(frame,(int(x),int(y)),(int(x+w),int(y+h)),(0,0,255),2)

    print("Total Cubes:{}".format(len(cubes)/4))
    table.putNumberArray("Cubes", cubes)
    return mask




# Cone Detector
coneLower = (5,80,180)
coneUpper = (235,180,230)

#image is the thing we are prossesing, frame is the thing we are drawing output on
def coneDetection(image, frame):
    mask = cv2.inRange(image, coneLower, coneUpper)
    mask = cv2.erode(mask, None, iterations = 2)
    mask = cv2.dilate(mask, None, iterations = 2)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(frame, contours, -3, (0,255,0), 2)
    cones = []
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        area = w*h
        if area > 300 and w/h < 2.0 and w/h > 0.5:
            cones += [x,y,w,h]
            cv2.rectangle(frame,(int(x),int(y)),(int(x+w),int(y+h)),(0,0,255),2)

    print("Total Cones:{}".format(len(cones)/4))
    table.putNumberArray("Cones", cones)
    return mask

# Main vision loop:
visionCycle = 0
mask = []

while(True):

   # print("[INFO] loading image...")
    # Capture frame-by-frame:
    ret, frame = capture.read()

   # LABframe = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    #mask = coneDetection(LABframe, frame)

    # Create greyscale image from input:
    if visionCycle == 0:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tagDetection(image, frame)

    if visionCycle == 1:
        LABframe = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        mask = cubeDetection(LABframe, frame)
        #frame = cv2.bitwise_and(frame, frame, mask = mask)

    if visionCycle == 2:
        LABframe = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        mask = coneDetection(LABframe, frame)
        #frame = cv2.bitwise_and(frame, frame, mask = mask)

   # if len(mask) > 0:
        # frame = cv2.bitwise_and(frame, frame, mask = mask)

    output.write(frame);
    visionCycle = visionCycle + 1

    if visionCycle > 2:
        visionCycle = 0

# When everything done, release the capture
capture.release()
output.release()

