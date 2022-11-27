import numpy as np
import cv2
import math

print cv2.CAP_GSTREAMER


# Capture Video and set resolution from gstreamer pipeline
capture_pipeline = "nvarguscamerasrc do-timestamp=true ! video/x-raw(memory:NVMM),format=(string)NV12,width=(int)1280,height=(int)720,framerate=60/1 ! nvvidconv flip-method=0 ! video/x-raw,width=(int)640,height=(int)360,format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink"
capture = cv2.VideoCapture(capture_pipeline)


# Video output streaming to gstreamer pipeline
output_pipeline = "appsrc ! videoconvert ! video/x-raw,format=(string)NV12 ! omxh264enc control-rate=2 bitrate=400000 profile=1 preset-level=1 ! video/x-h264, framerate=60/1, stream-format=(string)byte-stream ! h264parse ! rtph264pay config-interval=1 mtu=1000 ! udpsink host=%s port=%d" % ('127.0.0.1', 5801)

output = cv2.VideoWriter(output_pipeline, cv2.CAP_GSTREAMER, 60, (640,360))


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
    cv2.line(frame, (320,0), (320,360), (50,100,0), 2)
    cv2.line(frame, (0,180), (640,180), (50,100,0), 2)
    output.write(frame);
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
capture.release()
cv2.destroyAllWindows()
