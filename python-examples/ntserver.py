from networktables import NetworkTables
import time
import sys

NetworkTables.initialize()
sd = NetworkTables.getTable("Vision")

while True:
    time.sleep(10000) 
