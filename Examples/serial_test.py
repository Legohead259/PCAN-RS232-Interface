from PCAN_RS_232 import PCAN_RS_232

pcan = PCAN_RS_232('COM4', 57600)
print(pcan._ser.read_all())
print(pcan.set_auto_startup(False))
