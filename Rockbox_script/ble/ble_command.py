#python3
from server.server_config import *
from Time_parameter import *
from ble.simulation_device import *
from ble.Module.ble_Module import ble_Module
from ble.Module.encrypt import pass_function
import time, sys, os, datetime, random
from threading import Thread

class BLE_command():
	@staticmethod
	def get_raw_information(Update_manu,Update_rssi):
		if SIMULATION_BLE == 1:
			if band_Type == 1: # read by simulation_device.py
				try:
					#get info from simulation bands
					device = band1+band2 # simulation data from simulation_device.py
					device = map(list,zip(*[iter(device)]*len(band1))) # calibrate and list all information 
					device = {device[m][0]:device[m][1:] for m in range(len(device))} # use MAC address be main parameter.
					if Ble_debug == 1:
						print("simulation device is %s"%device)
					return ["OK",device]
				except Exception as e:
					print("problem? %s"%e)
					return ["Error",0]

			elif band_Type == 2: # read by test_device.txt files
				try:
					device = open("test_device.txt",'r').readlines()
					device = ble_Module.raw2dict(device)
					if device =="Error":
						return["Error",0]
					if Ble_debug == 1:
						print("simulation device is %s"%device)
					return ["OK",device]
				except Exception as e:
					if Ble_debug == 1:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
						print("Connection error : %s in line %s, %s"%(e, exc_tb.tb_lineno, fname))
					return ["Error",0]

		else:
			try:
				local_data = {}
				
				if len(Update_rssi)>0: # every SCAMTIME will take average rssi signal
					if Ble_debug == 1:
						print("Update rssi : %s"%Update_rssi)
						print("Update manu : %s"%Update_manu)
					for m in Update_rssi.keys():
						if len(Update_manu)>0:
							Update_mac.update(Update_manu)
						if Update_mac.get(m) != None:
							Update_mac.get(m).update({"rssi":int(sum(map(int,(Update_rssi.get(m).values()))) / len(Update_rssi.get(m).values())) })
					Update_rssi.clear() # if update mac already, will clean this Dict every time.
					Update_manu.clear() # if update Manufacturer already, will clean this Dict every time.
					if Ble_debug == 1:
						print("[BAND] Update mac : %s"%Update_mac)
					local_data = ble_Module.raw2dict(Update_mac) # raw data need to Modify
					Update_mac.clear()

				# local_data = device
				# filter low RSSI value
				[local_data.pop(m) for m in list(local_data) if int(local_data.get(m).get("rssi")) < FILTER_RSSI_VALUE]

				if len(temp_HT)>0: # Humidity sensor raw2dict
					for m in temp_HT.keys():
						if m not in Global_HT.keys():
							Global_HT.update({m:{}})
						if temp_HT.get(m).get("manu"):
							struct = temp_HT.get(m).get("manu").split()
							T_number = int(struct[1]+struct[0],16)/100
							H_number = int(struct[3]+struct[2],16)/100
							B_number = int(struct[7],16)
							# raw Humidity sensor data to Global sensor data.
							Global_HT.get(m).update({"temperature":T_number,"humidity":H_number,"batteryLevel":B_number,"rssi":temp_HT.get(m).get("rssi"),"scantime":int(time.time()),"manu":temp_HT.get(m).get("manu")})
					temp_HT.clear()
				if len(local_data) !=0:
					logger.debug("[Local data]\n%s\n"%local_data)
				if Ble_debug == 1:				
					print("[Global data]\n%s\n"%Global_data)

				if len(temp_sensor)>0: # for non-connect sensor use
					for m in list(temp_sensor):
						if "B4E782" in m: # use for VivaLNK thermometer
							manu = temp_sensor.get(m)[0].split()
							Tem_hex = int(manu[-2]+manu[-1],16)
							Battery_hex = int(manu[-3],16)
							Tem = (~Tem_hex & 0xffff)/16
							Battery = (~Battery_hex & 0xff)
							sensor_data.get("vivalnk").update({m:{"temperature":round(Tem,2),"batteryLevel":int(Battery),"scantime":temp_sensor.get(m)[2],"manu":temp_sensor.get(m)[0],"rssi":int(temp_sensor.get(m)[1])}})
					temp_sensor.clear()
				# check local_data structural integrity, if not will add "off" remark at last (Mark by 170301)
				# [local_data.pop(m) for m in local_data.keys() if (len(local_data.get(m))<3 or len(local_data.get(m))>3)]

				diffkeys = set(local_data.keys())-set(Global_data.keys()) # try to match local_data & global_data

				if len(diffkeys)>0: # new MAC address insert
					Global_data.update({m:local_data.get(m) for m in diffkeys})
					print("# of New insert : %s"%len(diffkeys))

				get_time = int(time.time()) # get right now time by system
				[local_data.get(m).update({"scantime":get_time,"scandatetime":time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(get_time))}) for m in local_data.keys()] # insert time to each key's value
				
				for m in local_data.keys(): # update RSSI and Manufacturer value from all broadcast BLE(not connect) to Global_data
					Global_data.get(m).update(local_data.get(m))
				if len(local_data)>0:
					return ["OK",0]
				else:
					return ["Error",0]
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				logger.warning("[BAND] Connection error : %s in line %s, %s"%(e, exc_tb.tb_lineno, fname))
				print("Update_mac :%s"%Update_mac)
				return ["Error", 0]

	@staticmethod
	def data_connect():
		try:
			# get device version info by raw mac
			Activation_data3 = {**Activation_data}
			# logger.debug("[Connect] Connect activation data \n%s"%Activation_data3)
			get_time = int(time.time())
			for m in list(Activation_data3):
				if "temperature" in list(Activation_data3.get(m)): # if get vivalnk sensor will skip
					continue
				#initial random time to let different box to connect
				if "BleV" not in list(Global_data.get(m)):
					Global_data.get(m).update({"AppV":[None,None],"BleV":[None,int(time.time())-Ble_Version_UPDATE_TIME+random.randint(200,300),None],"Battery":[None,int(time.time())-Ble_Battery_UPDATE_TIME+random.randint(200,300),None]})	
				if len(m) < 12:
					Global_data.pop(m)
					continue
				return_value = None
				if m in Global_data.keys():
					return_value = ble_Module.ble_get_version(time = get_time, mac = m)
				else:
					return_value = ble_Module.ble_get_version(time = get_time, mac = m, diff = 1)
				if return_value:
					if return_value !=1:
						Global_data.get(m).update(return_value)

			# for n in list(temp_sensor): # Connect device.
			# 	if not sensor_data.get(n):
			# 		return_value = None
			# 		if get_time - temp_sensor.get(n)[1] <= 10:
			# 			return_value = ble_Module.ble_get_version(time = get_time, mac = n, diff = 2)
			# 		if return_value:
			# 			if return_value !=1: # need to fix this
			# 				if not sensor_data.get(n):
			# 					sensor_data.update({n:{}})
			# 				sensor_data.get(n).update(return_value)

			# if Sensor_check.get("BPTriggered"): # check who is calling.
			# 	# print("check BPTriggered")
			# 	if len(Sensor_check.get("BPTriggered"))>1:
			# 		import operator
			# 		target_mac = max(Sensor_check.get("BPTriggered").iteritems(), key=operator.itemgetter(1))[0]
			# 	else:
			# 		target_mac = list(Sensor_check.get("BPTriggered"))[0]
			# 	# print("target mac %s"%target_mac)
			# 	if sensor_data:
			# 		Global_data.get(target_mac).update({"BloodPressure":sensor_data.get(list(sensor_data)[0])})
			# 	sensor_data.clear() # clear sensor_data after update bp data to global data
			# temp_sensor.clear()
			Activation_data3.clear()
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logger.warning("[data_connect] Wrong type error : %s in line %s, %s"%(e, exc_tb.tb_lineno, fname))

	@staticmethod
	def data_check():
		# here will write every T2 check Global_data status & if some expire data will return signal
		try:					
			check_time = int(time.time()) # get right now time by system
			for m in Global_data.keys():
				if check_time-Global_data.get(m).get("scantime")<CHECKTIME_EXPIRATION_TIME:
					Global_data.get(m).update({"Expire":"On"})

					if m not in Activation_data.keys():
						Activation_data.update({m:{}})
					# createtime = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
					createtime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"+00:00"
					Activation_data.get(m).update({
						"rssi":Global_data.get(m).get("rssi"),
						"createUtc":createtime,
						"relayMac":IoTBoxMAC.get("mac"),
						"sensorMac":m,
						# "mcuVersion":Global_data.get(m).get("AppV"),
						# "bleVersion":Global_data.get(m).get("BleV"),
						# "batteryLevel":Global_data.get(m).get("Battery"),
						"upTime":Global_data.get(m).get("upTime"),
						"sosAlertTriggered":Global_data.get(m).get("sosAlertTriggered"),
						"powerOnAlertTriggered":Global_data.get(m).get("powerOnAlertTriggered"),
						"powerOffAlertTriggered":Global_data.get(m).get("powerOffAlertTriggered"),
						"breakAwayAlertTriggered":Global_data.get(m).get("breakAwayAlertTriggered"),
						"highImpactAlertTriggered":Global_data.get(m).get("highImpactAlertTriggered"),
						"veryHighImpactAlertTriggered":Global_data.get(m).get("veryHighImpactAlertTriggered")
						})
					if not Global_data.get(m).get("sensorMac"):
						Global_data.get(m).update({"sensorMac":m})
					if not Global_data.get(m).get("BatteryBroadcastTime"):
						Global_data.get(m).update({"BatteryBroadcastTime":int(time.time())})			
					if Global_data.get(m).get("BleV"):
						if Activation_data.get(m).get("bleVersion"):
							Activation_data.get(m).pop("mcuVersion")
							Activation_data.get(m).pop("bleVersion")
						elif Global_data.get(m).get("AppV")[0] is not None:
							Activation_data.get(m).update({"mcuVersion":Global_data.get(m).get("AppV")[0],"bleVersion":Global_data.get(m).get("BleV")[0]})
						# else:# for CC2640
						# 	Activation_data.get(m).update({"bleVersion":Global_data.get(m).get("BleV")[0]})
					if Global_data.get(m).get("Battery"):
						if Activation_data.get(m).get("batteryLevel"):
							Activation_data.get(m).pop("batteryLevel")
						if Global_data.get(m).get("Battery")[0] is not None:
							if int(time.time())-Global_data.get(m).get("BatteryBroadcastTime")>300:
								Global_data.get(m).update({"BatteryBroadcastTime":int(time.time())})
								Activation_data.get(m).update({"batteryLevel":Global_data.get(m).get("Battery")[0]})
					if Global_data.get(m).get("NaccCount"): # with AccCount parameter
						# if int(time.time())-Global_data.get(m).get("accCountTime")>300: # every 5 mins will update to server.
						if Global_data.get(m).get("accCount"):
							if Global_data.get(m).get("accCount") != Global_data.get(m).get("NaccCount"):
								Global_data.get(m).update({"accCount":Global_data.get(m).get("NaccCount")})								
								Activation_data.get(m).update({"accCount":Global_data.get(m).get("accCount"),
																"more1G":Global_data.get(m).get("more1G"),
																"more2G":Global_data.get(m).get("more2G"),
																"more3G":Global_data.get(m).get("more3G")
																})
						else:
							Global_data.get(m).update({"accCount":Global_data.get(m).get("NaccCount")})
				else:
					Global_data.get(m).update({"Expire":"Off"})
					if m in list(Activation_data):
						Activation_data.pop(m)
			
			# check data for Humidity sensor.
			for m in Global_HT.keys():
				if check_time-Global_HT.get(m).get("scantime")<CHECKTIME_EXPIRATION_TIME:
					Global_HT.get(m).update({"Expire":"On"})
					if m not in Activation_HT.keys():
						Activation_HT.update({m:{}})
					createtime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"
					Activation_HT.get(m).update({
						"rssi":Global_HT.get(m).get("rssi"),
						"createUtc":createtime,
						"relayMac":IoTBoxMAC.get("mac"),
						"environmentalSensorMac":m,
						"humidity":Global_HT.get(m).get("humidity"),
						"temperature":Global_HT.get(m).get("temperature"),
						"batteryLevel":Global_HT.get(m).get("batteryLevel")
						})
				else:
					Global_HT.get(m).update({"Expire":"Off"})
					if m in list(Activation_HT):
						Activation_HT.pop(m)

			# use for vivalnk
			for m in list(sensor_data.get("vivalnk")):
				if check_time-sensor_data.get("vivalnk").get(m).get("scantime")<CHECKTIME_EXPIRATION_TIME:
					sensor_data.get("vivalnk").get(m).update({"Expire":"On"})
					if m not in list(Activation_data):
						Activation_data.update({m:{}})
					createtime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"
					Activation_data.get(m).update({
						"rssi":sensor_data.get("vivalnk").get(m).get("rssi"),
						"createUtc":createtime,
						"relayMac":IoTBoxMAC.get("mac"),
						"sensorMac":m,
						"temperature":sensor_data.get("vivalnk").get(m).get("temperature"),
						"batteryLevel":sensor_data.get("vivalnk").get(m).get("batteryLevel"),
						"temperatureUnit":"C" # by manually add
						})
				else:
					sensor_data.get("vivalnk").get(m).update({"Expire":"Off"})
					if m in list(Activation_data):
						Activation_data.pop(m)

			if CHECK_debug == 1:
				logger.info("[CGlobal data]\n%s\n"%Global_data)
				logger.info("[Activation data]\n%s\n"%Activation_data)
			return ["check_ok","reply"]			
		except Exception as e:
			if CHECK_debug == 1:
				logger.info("[ECGlobal data]\n%s\n"%Global_data)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logger.warning("[TCD] Wrong type error : %s in line %s, %s"%(e, exc_tb.tb_lineno, fname))
			wrong_signal = 404
			reply = "This is Reply."
			return [wrong_signal,reply]