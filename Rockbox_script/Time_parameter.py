## base on Python 3
## Time_parameter.py

Global_data = {}  
# Global data will be {'A1A2A3A4A5A6': {'data2': 'test_data2'}... , {'B1B2B3B4B5B6': {'data1': 'test_data1'}}..},
Activation_data = {} # Ble_command - check expire or not, if online will update to server
# Activation data will be {'A1A2A3A4A5A6': {'rssi': '-20',"Manufacturer":"ff 00 ..."}, 'B1B2B3B4B5B6': {'rssi': '-30'...}, ...}
Update_mac = {}
# will get device mac from ble and clean every SCANTIME seconds
Update_rssi = {} 
# every SCANTIME will average rssi value and clean every SCANTIME seconds
Update_manu = {}
# Manufacturer and clean every SCANTIME seconds
Block_mac = {} # block MAC list : if BLE name is not Rockband will block (blocklist) # list will be {'A1A2A3A4A5A6':{}}
# 170407 now just simple add development borad mac address white list here, 
DEV_WHITELIST = ["A12345678900"] # Dev white MAC list
Check_band_mac = "None" # use for check band in Activation_data and Global_data.

# Sensor_check = {"HT":False,"BPTriggered":{}} 
# HT:INKBIRD HT sensor, 
# BPTriggered: blood pressure sensor connect with target band trigger.

temp_sensor = {} # for broadcast sensor use, and same permission as band.
sensor_data = {"vivalnk":{}}

temp_HT = {} # Humidity sensor with broadcast, and use for environmentalSensorStatistics.
Global_HT = {} # global data for Humidity sensor.
Activation_HT = {} # Activation data for Humidity sensor

# Script version
Major_version = "1.0"
Script_version = ".190131"
Location_time = 8 # Asia:8, USA:-7~-9, JP:9
import os
systemlocation = os.path.dirname(os.path.abspath(__file__))

SCANTIME = 0.3
FILTER_RSSI_VALUE = -950 # in dBm
FILTER_RSSI_CONNECT = -85 # in dBm
CHECKTIME = 0.4
CHECKTIME_EXPIRATION_TIME = 10
UPDATETIME = 0.15

SIMULATION_BLE = 0 # 0 is off the simulation ble
Ble_debug = 0 # 0 is off ble debug mode
Ble_Battery_UPDATE_TIME = 3600 # BLE Battery update time in seconds
Ble_Version_UPDATE_TIME = 3600 # BLE Version update time in secondes (0 means only first time get version)
Ble_Version = {"connect":True}
CHECK_debug = 0 # 0 is off data check debug mode

SIMULATION_SERVER = 0 # 0 is off the simulation server
SS_debug = 0 # 0 is off server debug mode. if off 
SS_log = 1 # 1 is create server connect log files

IoTBox_dongle_miss = "" #server_command.py for check dongle is missing or not (every keep alive time will recheck again)
IoT_type = {"Type":"None"}

#http server
PORT_NUMBER = 8311
local_debug = 0

# log parameter
from logging.config import fileConfig
import logging
if SS_log ==1:
	location = os.path.dirname(os.path.abspath(__file__))
	log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log/log_config.ini')
	fileConfig(log_file_path,defaults={'location': location})
	logger = logging.getLogger("root")
	logger2 = logging.getLogger("scripthistory")
	logger3 = logging.getLogger("http_server")
else:
	from logging.config import dictConfig
	logging_config = dict(
	version = 1,
	formatters = {
	'f': {'format':'[%(levelname)s] %(asctime)s - %(message)s'}},
	handlers = {'h': {'class': 'logging.StreamHandler',
	'formatter': 'f','level': logging.DEBUG}},
	root = {'handlers': ['h'],'level': logging.INFO,},)
	dictConfig(logging_config)
	logger = logging.getLogger()
	logger2 = logging.getLogger()
	logger3 = logging.getLogger()