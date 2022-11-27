cd c:\gstreamer\1.0\x86_64\bin
gst-launch-1.0 -v udpsrc port=5802 ! "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! h264parse ! avdec_h264 ! timeoverlay ! autovideosink

