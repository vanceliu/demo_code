import sys,time,os,re,random
default_public_mac = "00:00:00:00:00:08"
try:
	sys.path.append(os.path.dirname(os.path.abspath(__file__)))
	from .pexpect_api import pexpect_gatt_connect,pexpect_gatt_command,pexpect_gatt_disconnect,pexpect_gatt_characteristics,pexpect_hcitool_disconnect
	from Time_parameter import *
except ImportError:
	from pexpect_api import pexpect_gatt_connect,pexpect_gatt_command,pexpect_gatt_disconnect,pexpect_gatt_characteristics,pexpect_hcitool_disconnect

# default_public_mac = "D0:FF:50:79:F7:BF"
debug = "on" # "off" will not show device version
test_sos_fd = "off"

def gatttool_api(*args):  # if no args will not return value
	os.system("killall -q -9 gatttool")
	pexpect_hcitool_disconnect()
	version_connect = None
	battery_connect = None
	if len(args) < 1:
		public_mac = default_public_mac
	elif len(args) == 1:
		public_mac = args[0]
	elif len(args) == 3:
		public_mac = args[0]
		version_connect = args[1]
		battery_connect = args[2]
	ctag = "both"
	if version_connect != "NaN":
		ctag = "version"
	elif battery_connect != "NaN":
		ctag = "battery"
	public_gatttool_handle = None
	version_value = None
	Firmware_value = None
	Software_value = None	
	Battery_value = None
	AA61_information = None
	return_structure = {public_mac:{}}
	restart = 0
	sub_con = None
	emergency_return_p = None
	connect_mac = public_mac.replace(":","")

	dongle_check = os.popen("hciconfig")
	hci_check = dongle_check.read()
	dongle_check.close()
	if "hci1" in hci_check:
		hci_connect = "hci1"
		os.system("hciconfig hci1 up")
	else:
		hci_connect = "hci0"
	
	if not Global_data.get(connect_mac):
		Global_data.update({connect_mac:{"Device_type":"CC2640"}})
	if Global_data.get(connect_mac).get("UUID"):
		public_gatttool_check = "Yes"
		public_gatttool_information = 1
	else:
		public_gatttool_check = None
		public_gatttool_information = None
	while restart<3:
		try:
			# create gatttool interface connection
			(sub_con,sub_re) = pexpect_gatt_connect(public_mac)
			if sub_con ==0:			
				logger.info("[Gatttool] device connection lost, or device busy. %s %s"%(public_mac[-5:],ctag))
				if version_connect:
					try: # delay 3~5 mins
						return_structure.get(public_mac).update({"AppV":[None,Global_data.get(public_mac).get("AppV")[1]],"BleV": [None,int(time.time())-Ble_Version_UPDATE_TIME+random.randint(200,300),Global_data.get(public_mac).get("BleV")[2]]})
					except:
						return_structure.get(public_mac).update({"AppV":[None,None],"BleV": [None,int(time.time())-Ble_Version_UPDATE_TIME+random.randint(200,300),None]})
				if battery_connect:
					try: # delay 3~5 mins
						return_structure.get(public_mac).update({"Battery":[None,int(time.time())-Ble_Version_UPDATE_TIME+random.randint(200,300),Global_data.get(public_mac).get("Battery")[2]]})
					except:
						return_structure.get(public_mac).update({"Battery":[None,int(time.time())-Ble_Version_UPDATE_TIME+random.randint(200,300),None]})
				# restart_dongle(hci_connect) # 170525 cancel restart dongle
				pexpect_hcitool_disconnect()
				os.system("killall -q -9 gatttool")
				return return_structure
			if not public_gatttool_check:
				if Global_data.get(connect_mac).get("Device_type") == "CC2541":
					# CC2541 version
					(sub_con,sub_re,uuid_list) = pexpect_gatt_characteristics(sub_con,["2a26","2a28","2a19","aa02","aa11","aa51","aa61"])
					if "UUID" not in list(Global_data.get(connect_mac)):
						Global_data.get(connect_mac).update({"UUID":{}})
					if sub_re =="Success":
						Global_data.get(connect_mac).get("UUID").update({"Firmware":uuid_list[0]})
						Global_data.get(connect_mac).get("UUID").update({"Software":uuid_list[1]})
						Global_data.get(connect_mac).get("UUID").update({"Battery":uuid_list[2]})
						Global_data.get(connect_mac).get("UUID").update({"AA02":uuid_list[3]})
						Global_data.get(connect_mac).get("UUID").update({"AA11":uuid_list[4]})
						Global_data.get(connect_mac).get("UUID").update({"AA51":uuid_list[5]})
						public_gatttool_information = 1
						if len(uuid_list)>6:
							Global_data.get(connect_mac).get("UUID").update({"AA61":uuid_list[6]})
							emergency_return_p = Global_data.get(connect_mac).get("UUID").get("AA61")					
						else:
							logger.warning("[Gatttool] Can't catch UUID-AA60.")
							emergency_return_p = None
					else:
						sub_con.close()
						os.system("killall -q -9 gatttool")
						return None
				elif Global_data.get(connect_mac).get("Device_type") == "CC2640":
					(sub_con,sub_re,uuid_list) = pexpect_gatt_characteristics(sub_con,["2a26","2a28","2a19"])
					if "UUID" not in list(Global_data.get(connect_mac)):
						Global_data.get(connect_mac).update({"UUID":{}})					
					if sub_re =="Success":
						Global_data.get(connect_mac).get("UUID").update({"Firmware":uuid_list[0]})
						Global_data.get(connect_mac).get("UUID").update({"Software":uuid_list[1]})
						Global_data.get(connect_mac).get("UUID").update({"Battery":uuid_list[2]})
						emergency_return_p = None
						public_gatttool_information = 1
					else:
						sub_con.close()
						os.system("killall -q -9 gatttool")
						return None

			if public_gatttool_information:
				if version_connect != "NaN": # if have version_connect get "NaN", will pass this script
					if sub_re =="Success":
						command = "char-read-hnd %s"%Global_data.get(connect_mac).get("UUID").get("Firmware")
						(sub_con,sub_re1,Firmware_value) = pexpect_gatt_command(sub_con,command,emergency = emergency_return_p,tag = 0)
					else:
						logger.debug("[gatttool] %s"%sub_re)
						Global_data.get(connect_mac).pop("UUID")
						public_gatttool_information = None
						pexpect_gatt_disconnect(sub_con)
						pexpect_hcitool_disconnect()
						os.system("killall -q -9 gatttool")
						continue
					
					if sub_re1 =="Success":
						command = "char-read-hnd %s"%Global_data.get(connect_mac).get("UUID").get("Software")
						(sub_con,sub_re2,Software_value) = pexpect_gatt_command(sub_con,command,emergency = emergency_return_p,tag = 0)
					else:
						logger.debug("[gatttool] %s"%sub_re)
						Global_data.get(connect_mac).pop("UUID")
						public_gatttool_information = None
						pexpect_gatt_disconnect(sub_con)
						pexpect_hcitool_disconnect()
						os.system("killall -q -9 gatttool")
						continue

					if (sub_re1=="Success" and sub_re2=="Success"):
						version_value = "None"
				if battery_connect != "NaN": # in restart timing, if have Battery value will pass the script
					if sub_re =="Success":
						command = "char-read-hnd %s"%Global_data.get(connect_mac).get("UUID").get("Battery")
						(sub_con,sub_re2,Battery_value) = pexpect_gatt_command(sub_con,command,emergency = emergency_return_p,tag = 1)
					else:
						logger.debug("[gatttool] %s"%sub_re)
						Global_data.get(connect_mac).pop("UUID")
						public_gatttool_information = None
						pexpect_gatt_disconnect(sub_con)
						pexpect_hcitool_disconnect()
						os.system("killall -q -9 gatttool")
						continue
				if version_connect and version_value:
					# 180A return structure
					return_structure.get(public_mac).update({"AppV":[Software_value.get("return"),Software_value.get("return")],"BleV": [Firmware_value.get('return'),int(time.time()),Firmware_value.get('return')]})					
					# AA01 return structure
					# return_structure.get(public_mac).update({"AppV":["%s.%s"%(int(info[5],16),int(info[6],16)),int(time.time())],
					# 										"BleV": "%s.%s"%(int(info[7],16),int(info[8],16))})
				if battery_connect and Battery_value:
					return_structure.get(public_mac).update({"Battery":[Battery_value.get('return'),int(time.time()),Battery_value.get('return')]})
					if Battery_value.get("SOS"):
						return_structure.get(public_mac).update({"sosAlertTriggered":True})
					if Battery_value.get("FD"):
						return_structure.get(public_mac).update({"fallAlertTriggered":True}) 
				# disconnect gatttool interface
				time.sleep(1)
				pexpect_gatt_disconnect(sub_con)
				pexpect_hcitool_disconnect()
				os.system("killall -q -9 gatttool")
				logger.info("[Gatttool] success get data %s %s"%(public_mac[-5:],ctag))
				return return_structure # return_structure = {public_mac : {"AppV": [0.00, time.time()], "BleV":0.00, "Battery": [00, time.time()]}}
			os.system("killall -q -9 gatttool")
			pexpect_hcitool_disconnect()
		except Exception as e:
			if sub_con:
				pexpect_gatt_disconnect(sub_con)
			pexpect_hcitool_disconnect()
			restart = restart + 1
			time.sleep(3)
			os.system("killall -q -9 gatttool")
			logger.warning("[Gatttool] Connection problem : %s (%s)"%(e,restart))
			if debug == "on":
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				logger.warning("problem : %s in line %s, %s"%(e, exc_tb.tb_lineno, fname))
	return {public_mac:"Connection error"}
	# if Global_data.get(public_mac).get("Battery"):
	# 	return_structure.get(public_mac).update({"Battery":[Global_data.get(public_mac).get("Battery")[0],int(time.time()),Global_data.get(public_mac).get("Battery")[2]]})
	# if Global_data.get(public_mac).get("BleV"):
	# 	return_structure.get(public_mac).update({"BleV":[Global_data.get(public_mac).get("BleV")[0],int(time.time()),Global_data.get(public_mac).get("BleV")[2]]})
	# return return_structure
def gatttool_api_fora(*args):
	os.system("killall -q -9 gatttool")
	pexpect_hcitool_disconnect()
	dongle_check = os.popen("hciconfig")
	hci_check = dongle_check.read()
	dongle_check.close()
	if "hci1" in hci_check:
		hci_connect = "hci1"
		os.system("hciconfig hci1 up")
	else:
		hci_connect = "hci0"
		
def restart_dongle(hci_connect):
	logger.warning("[DUMP] Reseting bluetooth dongle.")
	if hci_connect == "hci1":
		os.system("hciconfig hci1 down")
		time.sleep(5)
		os.system("hciconfig hci1 up")
		time.sleep(5)
	else:
		os.system("hciconfig hci0 down")
		time.sleep(5)
		os.system("hciconfig hci0 up")
		time.sleep(5)		
	# output = os.popen('lsusb')
	# match = [f for f in output.readlines() if "05e3" in f]
	# match = match[0].split()
	# os.system("usbreset /dev/bus/usb/%s/%s"%(match[1],match[3][:-1]))
	

# use for testing
def run():
	global debug,test_sos_fd,Global_data
	debug = "on" # "off" will not show device version
	Global_data = {}
	result = gatttool_api(default_public_mac,1,1)
	print(result)
if __name__=="__main__":
	run()

