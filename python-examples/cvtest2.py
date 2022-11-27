import numpy as np
import cv2
import math


# Capture Video and set resolution from gstreamer pipeline
capture_pipeline = "nvarguscamerasrc do-timestamp=true ! video/x-raw(memory:NVMM),format=(string)NV12,width=(int)1920,height=(int)1080,framerate=30/1 ! nvvidconv flip-method=0 ! video/x-raw,width=(int)640,height=(int)360,format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink"
capture = cv2.VideoCapture(capture_pipeline)


# Video output streaming to gstreamer pipeline
output_pipeline = "appsrc ! videoconvert ! video/x-raw,format=(string)NV12 ! omxh264enc control-rate=2 bitrate=400000 profile=1 preset-level=1 ! video/x-h264, framerate=30/1, stream-format=(string)byte-stream ! h264parse ! rtph264pay config-interval=1 mtu=1000 ! udpsink host=%s port=%d" % ('127.0.0.1', 5801)
output = cv2.VideoWriter(output_pipeline, cv2.CAP_GSTREAMER, 30, (640,360))


if capture.isOpened():
    print "Capture input pipeline created successfully..."
else:
    print "Capture input pipeline creation failed!"

if output.isOpened():
    print "Video output pipeline created successfully..."
else:
    print "Video output pipeline creation failed!"

# Blob detector parameters:
params = cv2.SimpleBlobDetector_Params()

# Change thresholds
params.minThreshold = 10
params.maxThreshold = 220

# Filter by Area.
params.filterByArea = True
params.minArea = 250
params.maxArea = 1200

# Filter by Circularity
params.filterByCircularity = True
params.minCircularity = 0.1

# Filter by Convexity
params.filterByConvexity = False
#params.filterByConvexity = True
#params.minConvexity = 0.87

# Filter by Inertia
params.filterByInertia = False
#params.filterByInertia = True
#params.minInertiaRatio = 0.1

# Filter by Color
#params.filterByColor = True


# NOTE: Bug in wrapper 
detector = cv2.SimpleBlobDetector_create(params)

while(True):

    # Capture frame-by-frame
    ret, frame = capture.read()
    
#    frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    keypoints = detector.detect(frame)
    frame = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    output.write(frame);

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
capture.release()
cv2.destroyAllWindows()
