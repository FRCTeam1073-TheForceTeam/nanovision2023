from networktables import NetworkTables
import sys
import time

#network number = 127.0.0.1

if len(sys.argv) < 2:
    print("Error: specify an IP to connect to!")
    exit(0)

#lets user set sys id (frc1073, 127.0.0.1)
ip = sys.argv[1]

NetworkTables.initialize(server=ip)

table = NetworkTables.getTable("Vision")

while True:
#    print("cam_0_bline")
#    print(table.getNumberArray("cam_0_bline", [-1]))
#    print("cam_1_wline")
#    print(table.getNumberArray("cam_1_wline", [-1]))
#    print("data_enable")
#    print(table.getBoolean("data_enable", False))
     print(table.getNumber("numTags", -1))
     time.sleep(1.0)
