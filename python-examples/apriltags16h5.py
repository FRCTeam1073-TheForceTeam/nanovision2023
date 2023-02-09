import numpy as np
import cv2
import math
import apriltag
from networktables import NetworkTables
import sys
import time


# Capture Video and set resolution from gstreamer pipeline
#capture_pipeline = "nvarguscamerasrc do-timestamp=true ! video/x-raw(memory:NVMM),format=(string)NV12,width=(int)1920,height=(int)1080,framerate=30/1 ! nvvidconv flip-method=0 ! video/x-raw,width=(int)640,height=(int)360,format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink emit-signals=True drop=true"#capture_pipeline = "nvarguscamerasrc do-timestamp=true ! video/x-raw(memory:NVMM),format=(string)NV12,width=(int)1920,height=(int)1080,framerate=30/1 ! nvvidconv flip-method=0 ! video/x-raw,width=(int)640,height=(int)360,format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink emit-signals=True drop=true"
capture_pipeline = "v4l2src device=/dev/video1 ! video/x-raw,format=(string)UYVY,width=(int)1280,height=(int)720,framerate=60/1 ! videorate max-rate=30 ! videoscale ! video/x-raw,width=(int)640,height=(int)360 ! videoconvert ! video/x-raw,format=(string)BGR ! appsink emit-signals=True drop=true"
capture = cv2.VideoCapture(capture_pipeline)

# Video output streaming to gstreamer pipeline
output_pipeline = "appsrc ! videoconvert ! video/x-raw,format=(string)NV12 ! omxh264enc control-rate=2 bitrate=400000 profile=1 preset-level=1 ! video/x-h264, framerate=30/1, stream-format=(string)byte-stream ! h264parse ! rtph264pay config-interval=1 mtu=1000 ! udpsink host=%s port=%d"%(sys.argv[1], 5801)

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

ip = "10.10.73.2"

# networktables.startClientTeam(1073)
# init network tables and "points" it at your robot [via robotpy]

NetworkTables.initialize(server=ip)

table = NetworkTables.getTable("Vision")
table.putNumber('Test', 32)
while(True):

   # print("[INFO] loading image...")
    # Capture frame-by-frame:
    ret, frame = capture.read()

    # Create greyscale image from input:
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
    output.write(frame);

# When everything done, release the capture
capture.release()
output.release()
