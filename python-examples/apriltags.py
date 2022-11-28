import numpy as np
import cv2
import math
import apriltag


# Capture Video and set resolution from gstreamer pipeline
capture_pipeline = "nvarguscamerasrc do-timestamp=true ! video/x-raw(memory:NVMM),format=(string)NV12,width=(int)1920,height=(int)1080,framerate=30/1 ! nvvidconv flip-method=0 ! video/x-raw,width=(int)640,height=(int)360,format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink emit-signals=True drop=true"
capture = cv2.VideoCapture(capture_pipeline)


# Video output streaming to gstreamer pipeline
output_pipeline = "appsrc ! videoconvert ! video/x-raw,format=(string)NV12 ! omxh264enc control-rate=2 bitrate=400000 profile=1 preset-level=1 ! video/x-h264, framerate=30/1, stream-format=(string)byte-stream ! h264parse ! rtph264pay config-interval=1 mtu=1000 ! udpsink host=%s port=%d"%('127.0.0.1', 5801)

output = cv2.VideoWriter(output_pipeline, cv2.CAP_GSTREAMER, 30, (640, 360))


if capture.isOpened():
    print("Capture input pipeline created successfully...")
else:
    print("Capture input pipeline creation failed!")

if output.isOpened():
    print("Video output pipeline created successfully...")
else:
    print("Video output pipeline creation failed!")

detectorOptions = apriltag.DetectorOptions(families="tag36h11")
detector = apriltag.Detector(detectorOptions)


while(True):

    # Capture frame-by-frame:
    ret, frame = capture.read()

    # Create greyscale image from input:
    image  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    tags = detector.detect(image);

    if len(tags) > 0:
        print("{} total tags detected".format(len(tags)))

    # Draw target lines over the video.
    for tag in tags:
        (ptA, ptB, ptC, ptD) = tag.corners;

        ptB = (int(ptB[0]), int(ptB[1]))
        ptC = (int(ptC[0]), int(ptC[1]))
        ptD = (int(ptD[0]), int(ptD[1]))
        ptA = (int(ptA[0]), int(ptA[1]))        
        
        cv2.line(frame, ptA, ptB, (50,100,0), 2)
        cv2.line(frame, ptB, ptC, (50,100,0), 2)
        cv2.line(frame, ptC, ptD, (50,100,0), 2)
        cv2.line(frame, ptD, ptA, (50,100,0), 2)

        (cX, cY) = (int(tag.center[0]), int(tag.center[1]))
        cv2.circle(frame, (cX,cY), 5, (0,0,255), -1)

        tagId = "{}".format(tag.tag_id)
        
        cv2.putText(frame, tagId, (ptA[0], ptA[1]-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        
    output.write(frame);

# When everything done, release the capture
capture.release()
output.release()
cv2.destroyAllWindows()
