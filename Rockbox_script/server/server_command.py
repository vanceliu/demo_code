## base on Python 3
import urllib, sys, os, time,subprocess, json, datetime
from threading import Timer,Event,Thread
from server.server_config import *
from server.Module.http_api import *
from Time_parameter import *
import logging

class server_command():
	@staticmethod
	def get_information(restart_check):
		try:
			global SERVER_check,SERVER_internet,SERVER_down,relay_login_time
			global IoTBox_dongle_miss,connect_status,iwconfig_connect_info,relay_ssh_time
			if SIMULATION_SERVER ==1:
				print("Check simulation is on")
				try:
					return "OK",200
				except Exception as e:
					print("Connection error : %s"%e)
					return "ERROR",404
			else:
				if relay_login_time and err_signal.get("signal")==200:
					relay_login_time2 = int(time.time())
					relay_ssh_time2 = int(time.time())
					if relay_login_time2 - relay_login_time>30: # every 30 second will check keep rockbox alive
						logger.debug("thread # %s"%threading.active_count())
						try:
							if audio_thread_check.get("canPlayAudio") == True:
								if audio_thread_check.get("check") == False:
									audio_thread_check.update({"check":True})
									Thread(target=server_command.check_audio_out).start()
								# audio_thread.join()
						except Exception as e:
							logger.warning("[AUDIO] Thread error with %s"%e)
						# IoTBox_running_time = subprocess.Popen("cat /proc/uptime",stdout = subprocess.PIPE,shell = True)
						IoTBox_running_time = os.popen("cat /proc/uptime")
						pattern_uptime = re.compile(r"(.*?) (.*?)")
						match_uptime = pattern_uptime.match(IoTBox_running_time.read())
						# IoTBox_running_time.kill()
						IoTBox_running_time.close()
						keep_parameter = {"upTime":str(int(float(match_uptime.group(1))/60))}

						logger.debug("IoT_type:%s"%IoT_type)
						if IoT_type.get("Type") =="new":
							ssh_check = os.popen("ps aux")
							ssh_check_read = ssh_check.read()
							if "ssh -o TCPKeepAlive=yes -o ServerAliveInterval=30 -N -f -R 0:localhost:22 iot-user@54.153.61.120" in ssh_check_read:
								ssh_check.close()
								pass
							else:
								logger.info("[SSH] Port restart.")
								try:
									# if ssh tunnel lost, will recreate ssh tunnel.
									import pexpect
									time.sleep(1)
									ssh_tunnel = pexpect.spawn("ssh -o TCPKeepAlive=yes -o ServerAliveInterval=30 -N -f -R 0:localhost:22 iot-user@54.153.61.120")
									time.sleep(4)
									ssh_tunnel.expect("localhost:22",timeout=60)
									# ssh_tunnel.expect(" for remote forward to localhost:22",timeout=5)
									ssh_tunnel_read = ssh_tunnel.before.decode("utf-8")
									logger.info("[SSH] %s"%ssh_tunnel_read)
									ssh_tunnel.close()
									IoT_type.update({"Type":"new"})
									if "not found" in ssh_tunnel_read:
										relayparams.update({"sshPort":"None"})
									else:								
										ssh_number = None
										ssh_number = re.findall(r"Allocated port (.*) for remote forward to ",ssh_tunnel_read)[0]
										if ssh_number:
											relayparams.update({"sshPort":ssh_number})
											relay_ssh_time = int(time.time())
								except Exception as e:
									logger.warning("[SSH] Problem :%s"%e)
						elif IoT_type.get("Type") =="old":
							pass
						[relay_status, relay_returnbody] = http_api.keepAlive(opener,"relay",keep_parameter,headers)
						if relay_status == 200:
							logger.info("[BOX] Relay still alive.")
							relay_login_time = int(time.time())
						else:
							err_signal.update({"signal":404})

						# check dongle is missing or not # need to check hci0 and hci1
						IoTBox_dongle = os.popen("hciconfig")
						if "hci0" in IoTBox_dongle.read():
							IoTBox_dongle.close()
							if IoTBox_dongle_miss == "_missing dongle":
								err_signal.update({"signal":404})
							IoTBox_dongle_miss = ""
						else:
							err_signal.update({"signal":404})
							IoTBox_dongle.close()
							IoTBox_dongle_miss = "_missing dongle"

				if SERVER_check >= 5:
					logger.warning("[SYSTEM] Fail relay login over 5 times.")
					# netstat
					logger.warning("Netstat the internet.")
					output4 = os.popen("netstat -rn")
					for f4 in output4.readlines():
						logger.warning(f4.replace("\n",""))
					output4.close()
					# ping
					output2 = os.popen('ping 8.8.8.8 -w 5') # try to ping if internet is working.
					ping_string = None
					for f in output2.readlines():
						logger.warning(f.replace("\n",""))
						if "64 bytes from" in f:
							print(f)
							ping_string = f
						# if "5 packets transmitted" in f:
						#     logger.warning(f)

					if not ping_string: # if internet is dead 3 times will reboot system
						logger.warning("[SYSTEM] Internet is down.")
						SERVER_internet = SERVER_internet + 1
						SSS.update({"SERVER_internet":SERVER_internet})
						ping_string = None
					else:
						logger.warning("[SERVER] server is down.")
						SERVER_down = SERVER_down + 1
						SSS.update({"SERVER_down":SERVER_down})
					# traceroute api.aiportal.co
					logger.warning("[SYSTEM] Try to traceroute api.aiportal.co")
					output2.close()
					output3 = os.popen("traceroute api.aiportal.co")
					for f2 in output3.readlines():
						logger.warning(f2)
					output3.close()
					SERVER_check = 0 # after reset dongle will count to 0
				if SERVER_internet >= 1: # 1 times will reboot
					logger.warning("[SYSTEM] Internet is down, rebooting the system. wait 20 seconds")
					logger2.warning("[Reboot] Internet reboot in US PDT %s (Taiwan CST %s) Server: %s internet: %s"%((datetime.datetime.utcnow()- datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
						(datetime.datetime.utcnow()+ datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),SERVER_down,SERVER_internet))
					time.sleep(5)
					os.system("reboot")
				if (err_signal.get("signal") == 404):
					while restart_check <= 2: # if restart time over 3 will wait next period.
						try:
							# try to find ip address
							info = subprocess.Popen("ifconfig wlan0",stdout = subprocess.PIPE,shell = True,close_fds=True)
							info2 = []
							for i in range(3):
								info2.append(bytes.decode(info.stdout.readline()))
							try:
								IoTBox_ipaddr = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",info2[1])[0]
								info.kill()
							except Exception as e:
								info.kill()
								info2 = []
								info = subprocess.Popen("ifconfig eth0",stdout = subprocess.PIPE,shell = True,close_fds=True)
								for i in range(3):
									info2.append(bytes.decode(info.stdout.readline()))
								IoTBox_ipaddr = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",info2[1])[0]
								info.kill()

							# try to find firmware version
							IoTBox_fwver = Major_version+Script_version+IoTBox_dongle_miss

							#first check server connection status (can not use admin login)
							relayparams.update({"name":"Relay%s"%IoTBoxMAC.get("mac"),"password":IoTBoxMAC.get("mac"),"fwVersion":IoTBox_fwver,"ipv4Address":IoTBox_ipaddr})
							connect_time = str({"updatetime":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"+00:00"}).replace("'",'"')
							connect_iwconfig = str({"iwconfig":iwconfig_connect_info}).replace("'",'"')
							if "Main" in list(connect_status):
								connect_status2 = str(connect_status).replace("'",'"')
								relayparams.update({"ipv6Address":connect_time+','+connect_iwconfig+','+connect_status2})
							elif "Ethernet" in list(connect_status):
								connect_status2 = "Ethernet"
								relayparams.update({"ipv6Address":connect_time+','+connect_status2})
							
							# try to setting SSH tunnel to monitor server
							
							# check SSH is alive or not
							if "new" in IoT_type.get("Type"):
								ssh_check = os.popen("ps aux")
								ssh_check_read = ssh_check.read()
								if "ssh -o TCPKeepAlive=yes -o ServerAliveInterval=30 -N -f -R 0:localhost:22 iot-user@54.153.61.120" in ssh_check_read:
									ssh_check.close()
								else:
									try:
										# if ssh tunnel lost, will recreate ssh tunnel.
										import pexpect
										os.popen("killall ssh")
										time.sleep(1)
										ssh_tunnel = pexpect.spawn("ssh -o TCPKeepAlive=yes -o ServerAliveInterval=30 -N -f -R 0:localhost:22 iot-user@54.153.61.120")
										time.sleep(4)
										ssh_tunnel.expect("localhost:22",timeout=60)
										# ssh_tunnel.expect(" for remote forward to localhost:22",timeout=5)
										ssh_tunnel_read = ssh_tunnel.before.decode("utf-8")
										logger.info("[SSH] %s"%ssh_tunnel_read)
										ssh_tunnel.close()
										IoT_type.update({"Type":"new"})
										relay_ssh_time = int(time.time())
										if "not found" in ssh_tunnel_read:
											relayparams.update({"sshPort":"None"})
										else:								
											ssh_number = None
											ssh_number = re.findall(r"Allocated port (.*) for remote forward to ",ssh_tunnel_read)[0]
											if ssh_number:
												relayparams.update({"sshPort":ssh_number})
									except Exception as e:
										logger.warning("[SSH] Problem :%s"%e)
							elif "old" in IoT_type.get("Type"):
								pass
							else:
								try:
									# try to create ssh tunnel to remote server
									import pexpect
									os.popen("killall ssh")
									time.sleep(1)
									ssh_tunnel = pexpect.spawn("ssh -o TCPKeepAlive=yes -o ServerAliveInterval=30 -N -f -R 0:localhost:22 iot-user@54.153.61.120")
									time.sleep(4)
									ssh_tunnel.expect("localhost:22",timeout=60)
									# ssh_tunnel.expect(" for remote forward to localhost:22",timeout=5)
									ssh_tunnel_read = ssh_tunnel.before.decode("utf-8")
									logger.info("[SSH] %s"%ssh_tunnel_read)
									ssh_tunnel.close()
									IoT_type.update({"Type":"new"})
									relay_ssh_time = int(time.time())
									if "not found" in ssh_tunnel_read:
										relayparams.update({"sshPort":"None"})
									else:								
										ssh_number = None
										ssh_number = re.findall(r"Allocated port (.*) for remote forward to ",ssh_tunnel_read)[0]
										if ssh_number:
											relayparams.update({"sshPort":ssh_number})
								except pexpect.EOF as e:
									IoT_type.update({"Type":"new"})
									print(e)
								except Exception as e:
									IoT_type.update({"Type":"old"})
									logger.warning("[SSH] Problem :%s"%e)

							if SS_debug==1:
								logger.debug("[SERVER] Relay parameter : %s\n"%relayparams)
							[relaylogin_status, relaylogin_returnbody] = http_api.login(opener,"relay",relayparams,headers)
							if relaylogin_status == 200: # if server is alive will return OK
								relay_login_time = int(time.time())
								relay_login_time3 = int(time.time())
								err_signal.update({"signal":200})
								connect_status.clear()
								if "canPlayAudio" in list(relaylogin_returnbody):
									audio_thread_check.update({"canPlayAudio":relaylogin_returnbody.get("canPlayAudio")})
								return "OK",1
							else:
								logger.debug("[SERVER] status : %s and %s"%(relaylogin_status,relaylogin_returnbody))
								logger.warning("[SERVER] Can't connect to server. (Relay_login)(Restart time: %s)"%restart_check)
								time.sleep(3) # wait restart time 3 second enough?
								restart_check = restart_check + 1
								SERVER_check = SERVER_check + 1
								# return "Error",check_status
						except Exception as e:
							exc_type, exc_obj, exc_tb = sys.exc_info()
							fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
							logger.warning("[SERVER] Can't connect to server. %s in line %s, %s (Type_error)(Restart time: %s)"%(e,exc_tb.tb_lineno,fname,restart_check))
							time.sleep(3) # wait restart time 3 second enough?
							restart_check = restart_check + 1
							SERVER_check = SERVER_check + 1
					err_signal.update({"signal":404})
					return "Error",0
				elif err_signal.get("signal") == 200:
					return "OK",1
				else:
					err_signal.update({"signal":404})
					return "Error",0
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logger.warning("[TUD] problem %s in line %s, %s "%(e,exc_tb.tb_lineno,fname))
			return "Error",0

	@staticmethod
	def audio_init():
		S_B_check = {"S":False,"B":False}
		Beep = systemlocation+"/audio/BEEP.mp3"
		SBeep = systemlocation+"/audio/SHORTBEEP.mp3"
		# check Beep and short beep file is exist or not.
		logger.info("[AUDIO] audio initialize.")
		while True:
			Beep_file_test = os.popen('if [ -f %s ] ; then echo "yes" ; else echo "no" ; fi'%Beep).read()
			if "no" in Beep_file_test:
				bp_params = {'name':"BEEP"}
				[bp_status,bp_returnbody] = http_api.find(opener,"audio",bp_params,headers)
				if bp_status == 200:
					with open(Beep,'wb') as f:
						f.write(bp_returnbody.get("content"))
						S_B_check.update({"B":True})
				else:
					print(bp_returnbody)
			elif "yes" in Beep_file_test:
				S_B_check.update({"B":True})
			else:
				print("something wrong (BEEP)")


			SBeep_file_test = os.popen('if [ -f %s ] ; then echo "yes" ; else echo "no" ; fi'%SBeep).read()
			if "no" in SBeep_file_test:
				sbp_params = {'name':"SHORTBEEP"}
				[sbp_status,sbp_returnbody] = http_api.find(opener,"audio",sbp_params,headers)
				if sbp_status == 200:
					with open(SBeep,'wb') as f:
						f.write(sbp_returnbody.get("content"))
						S_B_check.update({"S":True})
				else:
					print(sbp_returnbody)
			elif "yes" in SBeep_file_test:
				S_B_check.update({"S":True})
			else:
				print("something wrong (SBEEP)")

			if S_B_check.get("S") == True and S_B_check.get("B") == True:
				audio_thread_check.update({"init":True})
				break
			time.sleep(1)
		logger.info("[AUDIO] audio initialize is done.")

	@staticmethod
	def check_audio_out():
		try:
			if audio_thread_check.get("init") == False:
				server_command.audio_init()
			frws_params = {'noAlertStatus': 'DONE','alertType': 'SOS', 'select': '["id","alertType"]'}
			[frws_status,frws_returnbody] = http_api.findRangeWithSelect(opener,"sensorAlert",frws_params,headers)
			if frws_status == 404:
				logger.debug("This relay is not support audio output")
			if frws_status == 200:
				frws_params = {'noAlertStatus': 'DONE','alertType': 'MISSING', 'select': '["id","alertType"]'}
				[frws_status,frws_returnbody2] = http_api.findRangeWithSelect(opener,"sensorAlert",frws_params,headers)
				frws_params = {'noAlertStatus': 'DONE','alertType': 'HIGH_IMPACT', 'select': '["id","alertType"]'}
				[frws_status,frws_returnbody3] = http_api.findRangeWithSelect(opener,"sensorAlert",frws_params,headers)
				frws_returnbody.extend(frws_returnbody2)
				frws_returnbody.extend(frws_returnbody3)
				import base64
				Beep = systemlocation+"/audio/BEEP.mp3"
				SBeep = systemlocation+"/audio/SHORTBEEP.mp3"
				testfileNameAlert = systemlocation+"/audio/testAlert.mp3"
				testfileNameSenior = systemlocation+"/audio/testSenior.mp3"
				testfileNameRelay = systemlocation+"/audio/testRelay.mp3"
				# test_path = "test.mp3"
				fbid_list = []
				audioFlag = False
				for fbid in frws_returnbody:
					# print(fbid.get("id"))
					fbid_list.append(fbid.get("id"))
					if fbid.get("id") not in list(audio_check.get("id")): # put new id in audio_check dict
						logger.debug("[AUDIO] %s is not in list, add to audio_list"%fbid.get("id"))
						audio_check.get("id").update({fbid.get("id"):{"time1":0,"time2":int(time.time())}})
					if fbid.get("alertType") =="SOS":
						if int(time.time()) - audio_check.get("id").get(fbid.get("id")).get("time1")>30: # check SOS still alerm id 30 seconds will trigger again.
							logger.debug("[AUDIO] SOS id %s is over 30 seconds."%fbid.get("id"))
							fbid_params = {"id":fbid.get("id")}
							[fbid_status,fbid_returnbody] = http_api.findById(opener,"sensorAlert",fbid_params,headers)
							if fbid_status == 200:
								audioList = fbid_returnbody.get("audioList")
								relayContent = b''
								seniorContent = b''
								sosContent = b''
								if audioList:
									for audio in audioList:
										if audio.get('audioType') == 'SENIOR_AUDIO':
											seniorContent = base64.b64decode(audio.get('content'))
											print("Senior_audio")
										if audio.get('audioType') == 'SOS_AUDIO':
											print("sos_audio")
											sosContent = base64.b64decode(audio.get('content'))
										if audio.get('audioType') == 'RELAY_AUDIO':
											print("relay_audio")
											relayContent = base64.b64decode(audio.get('content')) 
									try:
										if len(sosContent)>0:
											with open(testfileNameAlert, 'wb') as f:              
												f.write(sosContent)
										if len(seniorContent)>0:
											with open(testfileNameSenior, 'wb') as f:
												f.write(seniorContent) 
										if len(relayContent)>0:
											with open(testfileNameRelay, 'wb') as f:
												f.write(relayContent)
										print('successful Write')
									except Exception as e:
										print(e)
										print('Something went wrong!')
									try:
										#In order play three audio file
										#After one is finished, next one will start playing
										if audioFlag == False:
											omxp = os.system('sudo mpg321 -g 500 %s'%Beep)
											audioFlag = True
										elif audioFlag == True:
											omxp = os.system('sudo mpg321 -g 500 %s'%SBeep)
										if len(seniorContent)>0:
											omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameSenior)
										if len(sosContent)>0:
											omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameAlert)
										if len(relayContent)>0:
											omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameRelay)
										audio_check.get("id").get(fbid.get("id")).update({"time1":int(time.time())})
									except Exception as e:
										logger.warning(e)
										logger.warning("Maybe Rockbox is not support audio output")
					else:
						# if alerm less 1 hour, cycle is every 15 mins trigger alerm
						if int(time.time()) - audio_check.get("id").get(fbid.get("id")).get("time2")<=3600:
							if int(time.time()) - audio_check.get("id").get(fbid.get("id")).get("time1")>900: # check still alerm id 15 mins will trigger again.
								logger.debug("[AUDIO] id %s is over 15mins."%fbid.get("id"))
								fbid_params = {"id":fbid.get("id")}
								[fbid_status,fbid_returnbody] = http_api.findById(opener,"sensorAlert",fbid_params,headers)
								if fbid_status == 200:
									audioList = fbid_returnbody.get("audioList")
									relayContent = b''
									seniorContent = b''
									missingContent = b''
									highImpactContent = b''
									if audioList:
										for audio in audioList:
											if audio.get('audioType') == 'SENIOR_AUDIO':
												seniorContent = base64.b64decode(audio.get('content'))
												print("Senior_audio")
											if audio.get('audioType') == 'MISSING_AUDIO':
												print("missing_audio")
												missingContent = base64.b64decode(audio.get('content'))
											if audio.get('audioType') == 'HIGH_IMPACT_AUDIO':
												print("high_impact_audio")
												highImpactContent = base64.b64decode(audio.get('content')) 
											if audio.get('audioType') == 'RELAY_AUDIO':
												print("relay_audio")
												relayContent = base64.b64decode(audio.get('content')) 
										try:
											if len(missingContent)>0:
												with open(testfileNameAlert, 'wb') as f:              
													f.write(missingContent)
											if len(highImpactContent)>0:
												with open(testfileNameAlert, 'wb') as f:
													f.write(highImpactContent)
											if len(seniorContent)>0:
												with open(testfileNameSenior, 'wb') as f:
													f.write(seniorContent) 
											if len(relayContent)>0:
												with open(testfileNameRelay, 'wb') as f:
													f.write(relayContent)
											print('successful Write')
										except Exception as e:
											print(e)
											print('Something went wrong!')
										try:
											#In order play three audio file
											#After one is finished, next one will start playing
											if audioFlag == False:
												omxp = os.system('sudo mpg321 -g 500 %s'%Beep)
												audioFlag = True
											elif audioFlag == True:
												omxp = os.system('sudo mpg321 -g 500 %s'%SBeep)
											if len(seniorContent)>0:
												omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameSenior)
											if(len(missingContent)>0 or len(highImpactContent)>0):
												omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameAlert)
											if len(relayContent)>0:
												omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameRelay)
											audio_check.get("id").get(fbid.get("id")).update({"time1":int(time.time())})
										except Exception as e:
											logger.warning(e)
											logger.warning("Maybe Rockbox is not support audio output")
						# if still alerm over 1 hour, cycle change to 1 hour alerm.
						elif int(time.time()) - audio_check.get("id").get(fbid.get("id")).get("time2") > 3600:
							if int(time.time()) - audio_check.get("id").get(fbid.get("id")).get("time1")>3600: # check still alerm id 1 hour will trigger again.
								logger.debug("[AUDIO] id %s is over 1 hour."%fbid.get("id"))
								fbid_params = {"id":fbid.get("id")}
								[fbid_status,fbid_returnbody] = http_api.findById(opener,"sensorAlert",fbid_params,headers)
								if fbid_status == 200:
									audioList = fbid_returnbody.get("audioList")
									relayContent = b''
									seniorContent = b''
									missingContent = b''
									highImpactContent = b''
									if audioList:
										for audio in audioList:
											if audio.get('audioType') == 'SENIOR_AUDIO':
												seniorContent = base64.b64decode(audio.get('content'))
												print("Senior_audio")
											if audio.get('audioType') == 'MISSING_AUDIO':
												print("missing_audio")
												missingContent = base64.b64decode(audio.get('content'))
											if audio.get('audioType') == 'HIGH_IMPACT_AUDIO':
												print("high_impact_audio")
												highImpactContent = base64.b64decode(audio.get('content')) 
											if audio.get('audioType') == 'RELAY_AUDIO':
												print("relay_audio")
												relayContent = base64.b64decode(audio.get('content')) 
										try:
											if len(missingContent)>0:
												with open(testfileNameAlert, 'wb') as f:              
													f.write(missingContent)
											if len(highImpactContent)>0:
												with open(testfileNameAlert, 'wb') as f:
													f.write(highImpactContent)
											if len(seniorContent)>0:
												with open(testfileNameSenior, 'wb') as f:
													f.write(seniorContent) 
											if len(relayContent)>0:
												with open(testfileNameRelay, 'wb') as f:
													f.write(relayContent)
											print('successful Write')
										except Exception as e:
											print(e)
											print('Something went wrong!')
										try:
											#In order play three audio file
											#After one is finished, next one will start playing
											if audioFlag == False:
												omxp = os.system('sudo mpg321 -g 500 %s'%Beep)
												audioFlag = True
											elif audioFlag == True:
												omxp = os.system('sudo mpg321 -g 500 %s'%SBeep)
											if len(seniorContent)>0:
												omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameSenior)
											if(len(missingContent)>0 or len(highImpactContent)>0):
												omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameAlert)
											if len(relayContent)>0:
												omxp = os.system('sudo mpg321 -g 500 %s'%testfileNameRelay)
											audio_check.get("id").get(fbid.get("id")).update({"time1":int(time.time())})
										except Exception as e:
											logger.warning(e)
											logger.warning("Maybe Rockbox is not support audio output")
				# need to delete id is gone in audio_check dict.
				logger.debug("[AUDIO] database audio_check :%s"%audio_check)
				logger.debug("[AUDIO] fbidlist from server : %s"%fbid_list)
				if len(audio_check.get("id"))>0:
					for audio_id in list(audio_check.get("id")):
						if audio_id not in fbid_list:
							logger.debug("[AUDIO] audio_id %s is not in fbid_list, will pop out."%audio_id)
							audio_check.get("id").pop(audio_id)
			# print("Thread is down.")
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logger.warning("[AUDIO] problem %s in line %s, %s "%(e,exc_tb.tb_lineno,fname))
		audio_thread_check.update({"check":False})

	@staticmethod
	def check_wifi():
		try:
			wifi_element = None
			global iwconfig_connect_info
			# check IOT Box is use wifi connect
			iwconfig_information = os.popen("iwconfig")
			iwconfig_raw_list = iwconfig_information.readlines()
			iwconfig_information.close()
			for iwconfig_info in iwconfig_raw_list:
				if "Access Point: Not-Associated" in iwconfig_info: # Ethernet connection
					iwconfig_connect_info = "Ethernet"
					break
				if ("ESSID" in iwconfig_info or "Access" in iwconfig_info):
					if "off/any" in iwconfig_info:
						iwconfig_connect_info = "Ethernet"
						break
					iwconfig_info = iwconfig_info.split()
				elif ("Rx" in iwconfig_info or "Tx" in iwconfig_info):
					iwconfig_info = iwconfig_info.strip().split("  ")
				else:
					iwconfig_info = iwconfig_info.strip().split()
				for wifi_element in iwconfig_info:
					if "ESSID" in wifi_element:
						iwconfig_connect_info.update({"ESSID":wifi_element.split(":")[-1]})
						continue
					if re.findall(r"(\S[0-9a-fA-F]\:\S[0-9a-fA-F]\:\S[0-9a-fA-F]\:\S[0-9a-fA-F]\:\S[0-9a-fA-F]\:\S[0-9a-fA-F])",wifi_element):
						iwconfig_connect_info.update({"address":wifi_element})
						continue
					if ("Rx " in wifi_element or "Tx " in wifi_element):
						x = wifi_element.split(":")
						iwconfig_connect_info.update({x[0]:x[1]})
						continue
					if ("Invalid" in wifi_element or "Missed" in wifi_element):
						x = wifi_element.split(":")
						iwconfig_connect_info.update({x[0]:x[1]})

			duplicate_check = 0
			another_check = 0
			wifi_list = ""
			pass_ = False
			if not "Ethernet" in iwconfig_connect_info:
				iwlist = os.popen("iwlist wlan0 scanning |grep '"+iwconfig_connect_info.get("address")+"' -A 1000")
				iwlist_list = iwlist.readlines()
				try:
					for iwlist_element in iwlist_list:
						iwlist_element = iwlist_element.strip()
						iwlist_element = iwlist_element.replace(" ","")
						iwlistsplit = iwlist_element.split(":",1)
						if duplicate_check == 0:
							wifi_list = "Main"
						else:
							wifi_list = str(duplicate_check)
						if "Address" in iwlistsplit[0]:
							pass_ = False
							if not wifi_list in list(connect_status):
								connect_status.update({wifi_list:{}})
							if another_check == 0:
								if "WifiAddress" in list(connect_status.get(wifi_list)):
									duplicate_check = duplicate_check + 1
									if not str(duplicate_check) in list(connect_status):
										connect_status.update({str(duplicate_check):{}})
									wifi_list = str(duplicate_check)
									connect_status.get(wifi_list).update({"WifiAddress":iwlistsplit[1]})
								else:
									connect_status.get(wifi_list).update({"WifiAddress":iwlistsplit[1]})

						if "ESSID" in iwlistsplit[0]:
							if not iwlistsplit[1] == iwconfig_connect_info.get("ESSID"):
								connect_status.pop(str(duplicate_check))
								pass_ = True
							else:
								connect_status.get(wifi_list).update({"WifiESSID":iwlistsplit[1]})
						if "Protocol" in iwlistsplit[0]:
							if pass_ is False:
								connect_status.get(wifi_list).update({"Protocol":iwlistsplit[1]})
						if "Frequency" in iwlistsplit[0]:
							if pass_ is False:
								connect_status.get(wifi_list).update({"Frequency":iwlistsplit[1]})
						if "BitRates" in iwlistsplit[0]:
							if pass_ is False:
								connect_status.get(wifi_list).update({"BitRates":iwlistsplit[1]})
						if "Quality" in iwlistsplit[0]:
							if pass_ is False:
								Quality_match = re.findall(r"Quality=([0-9a-fA-F/]+)Signallevel=(.*)",iwlistsplit[0])
								connect_status.get(wifi_list).update({"Quality":Quality_match[0][0],"Signallevel":Quality_match[0][1]})
				except Exception as e:
					logger.warning(e)
					logger.warning("[WIFI] WIFI maybe lost.")
				iwlist.close()
			else:
				connect_status.clear()
				connect_status.update({"Ethernet":1})
			err_signal.update({"signal":404})
			time.sleep(WIFITIMECHECK)
		except Exception as e:
			if wifi_element:
				logger.debug("[WIFI] wifi_element %s"%wifi_element)
				logger.debug("[WIFI] iwconfig_info %s"%iwconfig_info)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logger.warning("[WIFI] problem %s in line %s, %s "%(e,exc_tb.tb_lineno,fname))

	@staticmethod
	def get_update():
		# here will write the information and update to server
		if SIMULATION_SERVER == 1:

			try:
				# simulation code to check scan data
				print ("simulation is on")
				if SS_debug == 1:
					# logger.info("update time : %s"%UPDATETIME)
					logger.info("[Activation data]\n%s \n"%Activation_data)
					# logger.info("http connecting : %s"%(http_conn))
					logger.info("[Global_data]\n%s \n "%Global_data)
				for m in list(Activation_data):
					if Activation_data.get(m).get("AppV")[0]:
						logger.info("App version is %s "%Activation_data.get(m).get("AppV")[0])
						Global_data.get(m).get("AppV")[0] = None
						Global_data.get(m).get("BleV")[0] = None
					if Activation_data.get(m).get("Battery")[0]:
						logger.info("Battery is %s \n"%Activation_data.get(m).get("Battery")[0])
						Global_data.get(m).get("Battery")[0] = None					
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]				
				print("Wrong type error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))
		else:
			try:
				if len(Activation_data) == 0:
					# logger.info("[SERVER] No working sensor and wait next update time.")
					return

				logger.debug("[BAND] Get # of Working MAC : %s"%len(Activation_data.keys()))
				logger.debug("[BAND] Activation data : \n%s"%Activation_data)
				if Check_band_mac in Activation_data.keys():
					logger.debug("[CB] Activation data check band : %s\n%s"%(Check_band_mac,Activation_data.get(Check_band_mac)))
					logger.debug("[CB] Globla data Check band : %s\n%s"%(Check_band_mac,Global_data.get(Check_band_mac)))

				if SSS_mode == 1:
					Activation_data2 = {"list":[]}
					for m in list(Activation_data):
						Activation_data2.get("list").append(Activation_data.get(m)) # use for update server

					# # createBatch method
					Batch = {}
					paramsU = json.dumps(Activation_data2)
					[sensorS_status, sensorS_returnbody2] = http_api.createBatch(opener,"sensorStatistics",paramsU,headers) # update API
					if sensorS_status==200:
						logger.debug("[SERVER] Update sensor Statistics to server.")

						for m in list(Activation_data):
							if Activation_data.get(m).get("temperature"): # if get vivalnk sensor will skip
								continue
							if Activation_data.get(m):
								if Activation_data.get(m).get("mcuVersion") is not None: # if got value from version keys, will celan this value after update to server.
									Global_data.get(m).get("AppV")[0] = None
									Global_data.get(m).get("BleV")[0] = None
								if Activation_data.get(m).get("batteryLevel") is not None: # if got value from battery keys, will celan this value after update to server.
									Global_data.get(m).get("Battery")[0] = None

					elif sensorS_status!=200:
						logger.warning("[SERVER] Update sensor Statistics error. (%s)"%sensorS_returnbody2)
						if "no session" in sensorS_returnbody2: # if got "no session", means relay login is out of date.
							err_signal.update({"signal":404})
							pass

					if Sensor_thread_check.get("check") == False:
						Sensor_thread_check.update({"check":True})
						Thread(target=server_command.sensor_update).start()

					# # old update for one by one
					# Activation_data2 = Activation_data
					# for m in list(Activation_data2):
					# 	if Activation_data2.get(m):
					# 		paramsU = []
					# 		# createtime = datetime.now().replace(tzinfo = GMT(1)).isoformat()
					# 		# createtime = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
					# 		# paramsU: update sensorStatistics parameter
							
					# 		[sensorS_status, sensorS_returnbody2] = http_api.create(opener,"sensorStatistics",Activation_data2.get(m),headers) # update API
					# 		if sensorS_status==200:
					# 			logger.info("[SERVER] Update sensor Statistics to server. %s"%m)
					# 			if Activation_data.get(m):
					# 				if Activation_data.get(m).get("mcuVersion") is not None: # if got value from version keys, will celan this value after update to server.
					# 					Global_data.get(m).get("AppV")[0] = None
					# 					Global_data.get(m).get("BleV")[0] = None
					# 				if Activation_data.get(m).get("batteryLevel") is not None: # if got value from battery keys, will celan this value after update to server.
					# 					Global_data.get(m).get("Battery")[0] = None
					# 		elif sensorS_status!=200:
					# 			logger.info("[SERVER] Update sensor Statistics error. %s (%s)"%(m,sensorS_returnbody2))
					# 			if "no session" in sensorS_returnbody2: # if got "no session", means relay login is out of date.
					# 				err_signal.update({"signal":404})
					# 				break


					Activation_data2.clear() # after update, will clean this duplicate data
			except AttributeError as e: # raise error when Activation data get 'NoneType' object has no attribute 'get'
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				logger.warning("[SERVER] Error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))
				logger.warning("[BAND] Device connection lost (Activation data got None)")
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				logger.warning("[SERVER] Error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))
				if err_signal.get("signal") == 200:
					err_signal.update({"signal":404})
	@staticmethod
	def sensor_update():
		try:
			logger.debug("[SENSOR_HT] Get # of Working HT Sensor : %s"%len(Activation_HT.keys()))
			logger.debug("[SENSOR_HT] Activation HT Sensor : \n%s"%Activation_HT)
			if len(Activation_HT) == 0:
				logger.debug("[SENSOR_HT] No working sensor and wait next update time.")
				Sensor_thread_check.update({"check":False})
				return

			Activation_HT2 = {"list":[]}
			for m in list(Activation_HT):
				Activation_HT2.get("list").append(Activation_HT.get(m)) # use for update server
			logger.debug("[SENSOR_HT] Activation HT2 : \n%s"%Activation_HT2)

			# createBatch method
			Batch = {}
			paramsHT = json.dumps(json.dumps(Activation_HT2.get("list")))
			# logger.debug("[SENSOR_HT] dumps \n%s"%paramsHT)
			[sensorHT_status, sensorHT_returnbody] = http_api.createBatch(opener,"environmentalSensorStatistics",paramsHT,headers) # update API
			if sensorHT_status==200:
				logger.debug("[SERVER] Update environmentalSensorStatistics to server.")
				
			elif sensorHT_status!=200:
				logger.warning("[SERVER] Update environmentalSensorStatistics error. (%s)"%sensorHT_returnbody)
				if "no session" in sensorHT_returnbody: # if got "no session", means relay login is out of date.
					err_signal.update({"signal":404})
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logger.warning("[SENSOR_HT] Error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))
		Activation_HT.clear()
		Sensor_thread_check.update({"check":False})