# Vision20

Nanovision code developed during the 2022-23 season

# Introduction

Nanovision is a new concept for the team where we utilize the new
Jetson Nano as a vision co-processor instead of Raspberry Pi. It is
sligtly more expensive but tremendously more powerful as a processor
and this can allow us to do more video /vision processing on the the
robot.

# Hardware Outline

## The Jetson Nano Developmenet Board
The hardware for the Nanovision setup is the off-the-shelf JetsonNano
baord, available for $99:

[The Jetson Nano Development Kit](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)

The NVIDIA website has a wealth of resources available for the boards
and full access requires you sign up for a free account.

## SD Card Storage
The baord requires a high-quality micro-SD card to be its "disk"
storage and for that we use the following cards:

[128GB SD Cards](https://www.amazon.com/gp/product/B06XWZWYVP/ref=ppx_yo_dt_b_asin_title_o06_s01?ie=UTF8&psc=1)

Given the extremely tough environment of living in an FRC robot we
don't recommend skimping on the cards or other hardware parts or they
may fail on you in a match.

## Robot Capable Power Supply
In order to survive being part of an FRC robot you need to provide
very solid, unwavering power to this co-processor and you have to do
this by using the board as a "custom circuit". It should have 18 Guage
power wires coming from a snap-breaker protected circuit to a local
power regulator on the board. The power on a robot is a very messy
environment and you need a steady 5VDC supply for the Jetson Nano.
For this we use the following buck-boost regulator board from Pololu
for about $15.	

[Buck/Boost Power Module](https://www.pololu.com/product/4082)

This allows the board to tolerate the huge power swings seen in a
defensive robot power system. This can only supply about 15W of power
to the Jetson Nano so you can't use its maximum capabilities without a
beefier power supply.

## Camera Modules
One cool part of the JetsonNano is that it is hardware compatible with
RaspberryPi Camera Modules and the clones out there. This gives you a
really nice collection of MIPI based camera modules that you can
choose from and flexibility to pick modules with different types of
lenses for different situations. We use a wide-angle lens setup on the
hardware MIPI camera port in our setups. We use the following basic
drive camera on the MIPI camera port in our setup:

[Jetson Nano / Raspberry Pi Wide Angle Camera](https://www.amazon.com/IMX219-160-Camera-Resolution-Degree-Angle-View-IMX219/dp/B07SQ92SC7/ref=sr_1_3?keywords=Jetson+Nano+Camera&qid=1569800148&s=electronics&sr=1-3)

The JetsonNano can also work with any USB/UVC compatible camera
modules and has 4x USB 3.0 ports for cameras or other things and it
has the horsepower to capture, compress, process and transmit many
video streams simultaneously.


## Development Case
We also recommend getting a development system for the desktop in
addition to any systems you embed into your robot setup. For these
there is an excellent desktop case that helps with experimentation and
camera development in a nice, clean package:

[Jetson Nano Development Case](https://www.amazon.com/gp/product/B07VWXP88M/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1)


# Software Outline

The Jetson Nano is an Ubuntu based Linux machine running Linux on the
ARMv8 or "64-bit ARM" architecture. Because of this it has an enormous
and powerful collection of open-source software available for it. The
details of software setup are included in our notes directory.

The Jetson Nano includes many specialized hardware "processing
accelerators" that allow you to do more than just the main processor
can do alone. These are accessed through libraries that support the
open-source Gstreamer-1.0 system.

## GStreamer Software
By using open-source and custom NVIDIA Gstreamer-1.0 plugins you can
use tools to create video capture and processing pipelines on your
JetsonNano setups.

Our first, basic setups for the JetsonNano are simply bash scripts
that use gst-launch-1.0 to launch a gstreamer pipeline of software
modules that take advantage of the hardware on the JetsonNano and
capture, compress and transmit video to our driver station very
efficiently. 

GStreamer is also available for windows and we load GStreamer onto our
driver station and have GStreamer scripts that allow us to view the
streams from our JetsonNano in real-time.


## Setup Information

We typically set up the systems with user and account based on the
team name for an easy-to-remember ability to log into the Jetsons for
development and maintenance.


# Environment/Package Installation

We install the following packages beyond the JetPack 4.6 image. Note that
an actual connection to the internet is required for this to work.

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install screen emacs git nano python3-pip ipython3


Once you're done installing packages (which can take a while to
get your system fully up-to-date). You can clean up the package
manager state by running:

    sudo apt-get autoremove





## Development Packages

The Jetson JetPack 4.6 version ships with OpenCV 4.x and Python
bindings. We install some additional packages that allow us
to interact with FRC robot systems and to locate April tags
in our code for the new marker system.

    sudo -H pip3 install pynetworktables
    sudo -H pip3 install apriltag


We can then use Python, OpenCV and the integration of OpenCV with
Gstreamer to create python applications that create input (and output)
gstreamer pipelines for capturing data from the primary MIPI camera or
web cameras, then apply OpenCV vision processing and overlay drawing
to the images in Python, and then send the results to the output
pipelien to have it compressed by accelerated hardware and sent out
for viewing.

The Python applications also make use of PyNetworkTables (The Python
implementation of FRC Network Tables) allowing our vision programs to
provide a Network Table interface to the main Robot Conrol program.

The NetworkTable interface allows us to have the operator select modes
of cameras, switch between overlays and allows our vision code to send
data to autonomy and operator assist commands.

# OpenCV Upgrade

The OpenCV shipped with the system image is very old and does not take
advantage of CUDA processing on the Jetson. There is a process
described on the website:

https://qengineering.eu/install-opencv-4.5-on-jetson-nano.html

This describes how to set up and build newer versions of OpenCV that
include CUDA hardware acceleration. This process takes a long time to
run, but we follow it and install OpenCV 4.5.5 to get faster CV
processing and access to the latest features of OpenCV in our code.



# Example Python Vision Processing program outline:

import numpy as np
import cv2
from networktables import NetworkTables

# Set up capture
# Capture video from gstreamer pipeline:
capture_pipeline = "< big string with gstreamer input pipeline> ! videoconvert ! video/x-raw,format=(string)BGR ! appsink"

capture = cv2.VideoCapture(capture_pipeline)

# Set up output
# Send output video to gstreamer pipeline:
output_pipeline = "appsrc ! videoconvert ! video/x-raw,format=(string)NV12 < big string with gstreamer output pipeline>"

# Set up the rate and frame size of the output pipeline here as well.
output = cv2.VideoWriter(output_pipeline, cv2.CAP_GSTREAMER, 30, (640, 360))


if capture.isOpened() and output.isOpened():
   print("Capture and output pipelines opened")
else
   print("Problem creating pipelines...")

# Connect to network tables server:
NetworkTables.initialize(server='127.0.0.1')

visionTable = NetworkTables.getTable("Vision")

# Main vision processing loop:
while(True):
	# Capture a frame:
	ret, frame = capture.read()

	# Do image processing, etc. operations in OpenCV
	# ...

	# Draw onto the frame using OpenCV
	cv2.line(frame, (320,0), (320,360), (50,100,0),2)


	# Send frame to compression pipeline:
	output.write(frame)

	# Check network tables for commands or inputs...
	# Send some data to the network table or read input from it.
	# For example:
	visionTable.setNumberArray("targetPos", [-1]))
	mode = visionTable.getString("VisionMode", 'default')

# Networking Requirements For Robot Configuration

WiFi must be turned off and disabled.

In the IPV4 settings for the first video server.

	IP address = 10.<TE>.<AM>.3
	netmask = 255.0.0.0

Ethernet connect to the robot when testing the cameras setup.


Note that all of your streaming video addresses and ports must conform
to the FRC robot rules for robot networking.


# Setting Up Video on Driverstation

You need to download and install the complete runtime version of
gstreamer for Windows first. The video playback works by creating and
configuring standard gstreamer video components. You can find
gstreamer here: https://gstreamer.freedesktop.org/

To test that the Jetson is functional, first adjust the network settings, then:

	1. Connect Jetson to robot ethernet (switch) and power from the PDP

	2. Connect cameras to the Jetson (USB)

	3. On a laptop (not DS), go to terminal and type ssh team1073@10.10.73.3
	to connect to the JetsonNano to ensure it is working. The password is "team1073".

	4. On the DS, go to "c:\gstreamer\1.0\x86_64\bin" from the home directory and run the following
	(which can be copied from the windowsplay.bat files):
	   	gst-launch-1.0 -v udpsrc port=5801 ! "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! h264parse ! avdec_h264 ! timeoverlay ! autovideosink

	5. If the pipeline runs, then drag windowsplay.bat and windowsplay2.bat to the UPPER RIGHT CORNER of the DS
	screen. If it does not run, fix it, and then complete this step. 		

Go to users/team1073/FRCWorkspace/vision20. In the scripts folder
there should be two files named "windowsplay" and "windowsplay2". Drag
the two files onto the UPPER RIGHT CORNER of the desktop screen
	
Depending on the setup, the gstreamer pipeline may need to be
modified. This will only be necessary if the type of camera changes,
the video feedback is not correctly oriented, or if the resolution
needs to be altered.

To run, double click on the programs while connected to the robot's
radio. Ensure that the Jetson is properly wired and has stable
ethernet connection.


# Setting up video servers to start automatically on Jetson

Once your code is developed and tested, you'll want to set up the
vision services to start automatically on the Jetson as part of your
robot startup.

The autostart directory contains several files that are
systemd service unit files. These need to be copied
to:

    sudo cp <service file> /etc/systemd/system

Now reload configurations:

    sudo systemctl daemon-reload

Now you enable the services you want enabled to auto-start:

    sudo systemctl enable <service name>


You can then check on services using:

    systemctl status <service name>


Note that the autostart files assume you are using user team1073 and
that you have checked out the vision repository on the nano system at:
/home/team1073/Projects/vision20

# AprilTag Detection on Robot & Driverstation with Jetson Nano

After making sure you have downloaded gstreamer, make sure you are connected to the robot.

	ping <robot server name>

Now ssh into the Jetson Nano to ping the camera server:

	ssh jetson@<robot server name>

Imput Jetson password: jetson

In a command prompt tab, open a local server on computer to run vision processing window:

	./ windowsplay.bat

Run the AprilTag detection program:

	python3 apriltag16h5.py <laptop IvP4 adress>

# Copy local changes to GitHub

You will need to make a copy of the changes made to python programs while connected to the robot and jetson nano. To copy these files onto your computer in order to upload them to GitHub:

	cd <camera file>
	scp jetson@<camera server name> : /<file source> .

Remember to commit these changes to GitHub after copying them onto your computer. 
