import numpy as np
import cv2
import math


# Capture Video and set resolution from gstreamer pipeline
capture_pipeline = "v4l2src device=%s ! video/x-raw,format=(string)YUY2, width=(int)320, height=(int)240, framerate=30/1 ! videoconvert ! video/x-raw,format=(string)BGR ! appsink" % ('/dev/video1')

capture = cv2.VideoCapture(capture_pipeline)

# Video output streaming to gstreamer pipeline
output_pipeline = "appsrc ! videoconvert ! video/x-raw,format=(string)NV12 ! omxh264enc control-rate=2 bitrate=400000 profile=1 preset-level=1 ! video/x-h264, framerate=30/1, stream-format=(string)byte-stream ! h264parse ! rtph264pay config-interval=1 mtu=1000 ! udpsink host=127.0.0.1 port=5802"

output = cv2.VideoWriter(output_pipeline, cv2.CAP_GSTREAMER, 30, (320,240))


if capture.isOpened():
    print "Capture input pipeline created successfully..."
else:
    print "Capture input pipeline creation failed!"

if output.isOpened():
    print "Video output pipeline created successfully..."
else:
    print "Video output pipeline creation failed!"

while(True):

    # Capture frame-by-frame
    ret, frame = capture.read()
    # Draw target lines over the video.
    cv2.line(frame, (160,0), (160,240), (50,100,0), 2)
    cv2.line(frame, (0,120), (320,120), (50,100,0), 2)
    output.write(frame);
    
    frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(frame2, 50, 150, None, 3)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
capture.release()
cv2.destroyAllWindows()
