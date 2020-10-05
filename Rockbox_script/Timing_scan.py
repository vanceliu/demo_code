## base on Python 3
import datetime
import time, sys, os, subprocess, traceback
from threading import Timer,Event,Thread
from ble.ble_command import BLE_command
from ble.Module.ble_Module import ble_Module
from server.server_command import server_command
from server.server_config import *
from Time_parameter import *
from http_server import myHandler
def Time_schedule_scan():
	# Global_data init. is in Time_parameter.py
	stopped = Event()
	def _time_scan_device():
		# 1-a. get device information.
		# 2. every T1 second  will san bands data and get intersity
		starttime = int(time.time())
		while not stopped.wait(SCANTIME):
			try:
				# print("thread # %s"%threading.active_count())
				[return_signal,information] = BLE_command.get_raw_information(Update_manu,Update_rssi)
				if return_signal == "OK":
					nowtime = int(time.time())
					if nowtime - starttime >60:
						# logger.info("[ScanThread] still alive")
						starttime = nowtime
			except Exception as e:
				logger.warning("[ScanThread] Wrong information : %s"%e)

			# 	continue
		logger.warning("[ScanThread] _time_scan_device thread is Stock.")
	
	def _time_connect_device():
		time.sleep(5) # wait if get activation_data at startup
		while not stopped.wait(5):
			try:
				if Ble_Version.get("connect") is True:
					# 1. first get global data, and raw scan data.
					# 2. each new device will connect 
					BLE_command.data_connect()	
			except Exception as e:
				logger.warning("[ConnectThread] %s"%e)
		logger.warning("[ConnectThread] _time_connect_device thread is Stock.")
	
	def _time_check_data():
		# every T2 second wiil detect data to check expire
		time.sleep(3)
		while not stopped.wait(CHECKTIME):
			# find fall data is uncomplete.
			try:
				[return_signal,reply] = BLE_command.data_check()
				if CHECK_debug == 1:
					print("Return signal is %s"%return_signal)
				# 1. xcheck server status is busy or not if have fall detect
				# 2. reply server.
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				logger.info("[CheckThread] Lost? : %s in line %s, %s"%(e, exc_tb.tb_lineno, fname))
		logger.warning("[CheckThread] _time_check_data thread is Stock.")

	def _time_update_data():
		time.sleep(2)
		while not stopped.wait(UPDATETIME):
			try:
				# 2. every T3 second will update tempdata to server
				restart_check = 1
				# check server is busy or not (or anything else)
				check_server_alive = server_command.get_information(restart_check)
			except Exception as e:
				logger.warning("[UpdateThread] Problem : %s"%e)
				check_server_alive = ["wrong!",0]
			finally:
				if check_server_alive[0] == "OK":
					server_command.get_update()
				else:
					if err_signal.get("Add") == 0:
						logger.info("[UpdateThread] No device found")
					else:
						logger.info("[UpdateThread] Server connection lost.")
		logger.warning("[UpdateThread] _time_update_data thread is Stock.")

	def _http_server():
		try:
			myHandler.run()
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logger3.warning("[HTTP] Problem : %s in line %s"%(e, exc_tb.tb_lineno))
			_http_server()
	def _sync_ntp_time():
		while not stopped.wait(1):
			# if int((datetime.datetime.utcnow()+datetime.timedelta(hours=Location_time)).strftime("%H"))%24 == 0:
			try:
				trytosync = os.popen("ntpdate -s -d time.nist.gov")
				# trytosync = os.popen("ntpdate 192.100.0.126")
				if "receive" in trytosync.read():
					trytosync.close()
					logger.info("[SYSTEM] _sync_ntp_time is finished.")
					time.sleep(86400)
					# break
				else:
					logger.info("[SYSTEM] Fail to sync ntp time")
					trytosync.close()
			except Exception as e:
				logger.warning("[_sync_time] Error as %s."%e)

	def _wifi_check():
		while not stopped.wait(1):
			logger.info("[WIFI] Wifi checking.")
			check_wifi = server_command.check_wifi()
	def ble_api():
		while not stopped.wait(20):
			try:
				ble_Module.ble_api_v3()
			except:
				logger.warning("[DUMP] ble_api is stopping. will restart in 20 second.")
	def _time_lescan():
		logger.info("[DUMP] Initial trigger lescan")
		os.popen("hciconfig hci0 reset")
		time.sleep(2)
		os.popen("hcitool -i hci0 lescan --duplicates")
		while not stopped.wait(2):
			os.popen("hciconfig hci0 reset")
			time.sleep(2)
			try_hcitool = os.popen("hcitool -i hci0 lescan --duplicates")
			hciconfig_check = os.popen("hciconfig hci0")
			if "DOWN" in hciconfig_check.read():
				logger.warning("[DUMP] hci0 Network is down")
				continue
			else:
				logger.info("[DUMP] trigger lescan loop")
			hcitool_time = int(time.time())
			hcitool_time2 = int(time.time())
			while (hcitool_time2-hcitool_time)<600:
				time.sleep(5)
				hcitool_check = os.popen("ps aux|grep hcitool").readlines()
				if len(hcitool_check)>2:
					hcitool_time2 = int(time.time())
					continue
				else:
					hcitool_time2 = hcitool_time+601
	T1 = Thread(target=_time_scan_device)
	T1.start()
	T2 = Thread(target=_time_check_data)
	T2.start()
	T3 = Thread(target=_time_update_data)
	T3.start()
	T4 = Thread(target=_time_connect_device)
	T4.start()
	T5 = Thread(target=_http_server)
	T5.start()	
	Thread(target=_sync_ntp_time).start()
	Thread(target=_wifi_check).start()
	T6 = Thread(target=ble_api)
	T6.start()
	T7 = Thread(target=_time_lescan)
	T7.start()
	while True:
		print("check Thread is alive")
		if not T1.is_alive():
			logger.warning("[Main] _time_scan_device thread is Dead, will try to restart.")
			T1 = Thread(target=_time_scan_device)
			T1.start()
		if not T2.is_alive():
			logger.warning("[Main] _time_check_data thread is Dead, will try to restart.")
			T2 = Thread(target=_time_check_data)
			T2.start()
		if not T3.is_alive():
			logger.warning("[Main] _time_update_data thread is Dead, will try to restart.")
			T3 = Thread(target=_time_update_data)
			T3.start()
		if not T4.is_alive():
			logger.warning("[Main] _time_connect_device thread is Dead, will try to restart.")
			T4 = Thread(target=_time_connect_device)
			T4.start()
		if not T5.is_alive():
			logger.warning("[Main] _http_server thread is Dead, will try to restart.")
			T5 = Thread(target=_http_server)
			T5.start()
		if not T6.is_alive():
			logger.warning("[Main] ble_api thread is Dead, will try to restart.")
			T6 = Thread(target=ble_api)
			T6.start()
		if not T7.is_alive():
			logger.warning("[Main] _time_lescan thread is Dead, will try to restart.")
			T7 = Thread(target=_time_lescan)
			T7.start()
		time.sleep(30)
	return stopped.set

def run():
	logger.info("[SYSTEM] System start up, Timing_scan project. Ver %s%s"%(Major_version,Script_version))
	time.sleep(10)
	logger2.info("[Boot] Time : US PDT %s (Taiwan CST %s)"%((datetime.datetime.utcnow()- datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
		(datetime.datetime.utcnow()+ datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")))
	while True:
		call = Time_schedule_scan()

if __name__=="__main__":
	run()