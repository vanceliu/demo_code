import pexpect,time,sys,os

def rssi_test(mac):
	restart = 1
	while True:
		try:
			R = []
			scan = pexpect.spawn("hcitool lescan --passive --duplicates")
			child = pexpect.spawn("hcidump -a")
			for i in range(0,3):
				child.expect("bdaddr %s"%mac,timeout = 5)
				R_valueO = child.readline()[:-2].decode()
				child.expect("RSSI: ",timeout = 5)
				R_value = child.readline()[:-2].decode()
				R.append(int(R_value))
			child.send('\003')
			try: #python3
				from statistics import mean
			except: #python2
				def mean(l):
					return reduce(lambda x, y: x + y, l) / len(l)
			average = mean(R)
			rssi_value = int(average)
			scan.close()
			child.close()
			return rssi_value
		except Exception as e:
			print(e)
			print("rssi wrong")
			child.close()
			time.sleep(1)
			restart = restart + 1
			pexpect_hcitool_disconnect()
			if restart>3:
				break

def pexpect_gatt_connect(mac,*args):
	restart = 1
	dongle_check = os.popen("hciconfig")
	hci_check = dongle_check.read()
	dongle_check.close()
	if "hci1" in hci_check:
		hci_connect = "hci1"
	else:
		hci_connect = "hci0"
	while True:
		if len(args)>0:
			child = args[0]
			try:
				child.sendline("gatttool -i %s -b %s -I"%(hci_connect,mac)) # create child function
				child.sendline("connect")
				child.expect("Connection successful", timeout=5)
				print("Success connect device %s"%mac)
				return(child,"Success")
			except Exception as e:
				# child.sendline("exit")
				child.close()
				# restart = restart + 1
				# if restart > 3:
				return(0,e)
		else:
			try:
				child = pexpect.spawn("gatttool -i %s -b %s -I"%(hci_connect,mac))
				child.sendline("connect")
				child.expect("Connection successful", timeout=5)
				print("Success connect device %s"%mac)
				return(child,"Success")
			except Exception as e:
				# child.sendline("exit")
				child.close()
				# restart = restart + 1
				# if restart > 3:
				return(0,e)

def pexpect_gatt_command(child,command,**kwargs):
	production_test = None
	notification = None
	emergency = None
	debug = None
	tag = None
	if kwargs:
		for kwarg in list(kwargs):
			if "emergency" == kwarg:
				emergency = kwargs.get(kwarg)
			if "tag" == kwarg:
				tag = kwargs.get(kwarg)
			if "production_test" == kwarg:
				production_test = kwargs.get(kwarg)
			if "notification" == kwarg:
				notification = kwargs.get(kwarg)
			if "debug" == kwarg:
				debug = kwargs.get(kwarg)
	R_status = {}
	if not production_test:   # normal send command.
		try:
			child.sendline(command)
			# child.expect("Characteristic value was written successfully",timeout=2)
			if notification:
				child.expect("Notification handle = %s value: "%notification, timeout=1)
			else:
				child.expect("Characteristic value/descriptor: ", timeout=3)
		except Exception as e:
			if not tag:
				return(child,"No Response.",0)
		else:
			if notification:
				R_valueO = child.readline()[:-3].decode().split()
				if R_valueO[0] =="1d": #battery
					R_value = int(R_valueO[1],16)
				if R_valueO[0] =="6a": #flash
					R_value = bytearray.fromhex(R_valueO[1]+R_valueO[2]).decode()
				if R_valueO[0] =="65": #Cap sensor
					R_value = int(R_valueO[2]+R_valueO[1],16)
				R_status.update({"return":R_value,"raw":R_valueO})
			else:
				R_valueO = child.readline()[:-3].decode()
				if len(R_valueO)==2:
					R_value = int(R_valueO,16)
				else:
					R_value = bytearray.fromhex(R_valueO).decode()
				R_status.update({"return":R_value})
		if tag ==1:
			try:
				child.expect("Notification handle = %s value: "%emergency, timeout=1)
			except Exception as e:
				R_status.update({"powerOn":"FF","powerOff":"FF"})
			else:
				try:
					alert = child.readline()[:-3].decode().split()
					if alert[0] == "01":
						R_status.update({"FD":"01"})
					if alert[3] == "01":
						R_status.update({"SOS":"01"})
					if len(alert) >=6:
						if alert[4] == "01":
							R_status.update({"powerOn":"01","powerOff":"FF"})
						elif alert[4] =="08":
							R_status.update({"powerOn":"FF","powerOff":"01"})
						else:
							R_status.update({"powerOn":"FF","powerOff":"FF"})
				except:
					R_status.update({"powerOn":"FF","powerOff":"FF"})
		return (child,"Success",R_status)
	if production_test: # in production test send command
		restart =1
		if debug:
			if debug =="ON":
				print("tag = %s"%tag)
		while True:		
			try:
				structure = []
				child.sendline(command)
				if debug =="ON":		
					print(command)
				# time.sleep(1)
				try:
					# get raw data
					for i in range(0,30):
						index = child.expect("Notification handle = %s value: "%production_test,timeout = 5)
						struct = child.readline()[:-3].decode().split()
						# print(struct)
						if tag ==1: # device_Accelerometer
							if index == 0:
								structlen = divmod(len(struct),6)
								for i in range(0,structlen[0]):
									if struct[0] == "60":
										X = int(struct[2+i*6]+struct[1+i*6],16) 
										Y = int(struct[4+i*6]+struct[3+i*6],16)
										Z = int(struct[6+i*6]+struct[5+i*6],16) 
										if X>=32768:
											X = -65536+X
										if Y>=32768:
											Y = -65536+Y
										if Z>=32768:
											Z = -65536+Z
										structure.append([X,Y,Z])
									else:
										pass
							if len(structure) >= 32:
								break
						elif tag ==2: #device_Magneticsensor
							if index ==0:
								structlen = divmod(len(struct),8)
								for i in range(0,structlen[0]):
									if struct[0] == "61":
										X = int(struct[2+i*8]+struct[1+i*8],16) 
										Y = int(struct[4+i*8]+struct[3+i*8],16)
										Z = int(struct[6+i*8]+struct[5+i*8],16)
										R = int(struct[8+i*8]+struct[7+i*8],16)
										if X>=32768:
											X = -65536+X
										if Y>=32768:
											Y = -65536+Y
										if Z>=32768:
											Z = -65536+Z
										if R>=32768:
											R = -65535+R
										structure.append([X,Y,Z,R])
									else:
										pass
							if len(structure) >= 32:
								break
					# average data
					if debug =="ON":
						print(structure)
					totallen = len(structure)
					total_value_list = [sum(x) for x in zip(*structure)]
					average_value_list = [int(x/totallen) for x in total_value_list]
					return_value = {"return":average_value_list,"len":totallen,"raw":structure}

				except pexpect.TIMEOUT as e:
					if debug:
						if debug =="ON":				
							print(e)
							print(len(structure))
					restart = restart + 1
					if restart >3:
						return(child,"Error",0)							
					continue
				return(child,"Success",return_value)
			except Exception as e:
				if debug:
					if debug =="ON":
						print(e)
				time.sleep(1)
				restart = restart + 1
				if restart >3:
					return(child,"Error",0)

def pexpect_gatt_chardesc(child,uuids):
	uuidlen = len(uuids)
	restart =1
	returnhandle = [None]*uuidlen
	while True:
		try:
			child.sendline("char-desc")
			while True:
				if None not in returnhandle: # if all element in list have value will break while loop.
					break
				index = child.expect("handle: ",timeout = 10)
				R_value = child.readline()[:-3].decode()
				for i in range(len(uuids)): # find each uuid's handle
					if returnhandle[i] !=None:
						continue
					elif uuids[i] in R_value:
						returnhandle[i] = R_value.split(", ")[0]
			return(child,"Success",returnhandle)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))
			restart = restart+1
			time.sleep(1)
			if restart>3:
				return(child,"Error",0)

def pexpect_gatt_characteristics(child,uuids):
	uuidlen = len(uuids)
	restart =1
	returnhandle = [None]*uuidlen
	while True:
		try:
			child.sendline("characteristics")
			while True:
				if None not in returnhandle: # if all element in list have value will break while loop.
					break
				index = child.expect("char value handle: ",timeout = 10)
				R_value = child.readline()[:-3].decode()
				for i in range(len(uuids)): # find each uuid's handle
					if returnhandle[i] !=None:
						continue
					elif uuids[i] in R_value:
						returnhandle[i] = R_value.split(", ")[0]
			return(child,"Success",returnhandle)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))
			if "Bad file descriptor" in e:
				return(child,"Error",0)
			restart = restart+1
			time.sleep(1)
			if restart>3:
				return(child,"Error",0)

def pexpect_gatt_disconnect(child,*args):
	keep = None
	if len(args)>0:
		keep = args[0]
	if keep:
		try:
			child.sendline("disconnect")
			print("Success disconnect device")
			return(child,"Success")
		except Exception as e:
			return(child,"Can't disconnect")
	else:
		try:
			child.sendline("disconnect")
			time.sleep(0.5)
			child.sendline("exit")
			child.close()
			print("Success disconnect device")
			#child.expect(" ")
		except Exception as e:
			return(0,"Can't disconnect")
		else:
			return(1,"Success")

def pexpect_hcitool_disconnect(**kwargs):
	debug = None
	if kwargs:
		for kwarg in list(kwargs):
			if "debug" == kwarg:
				debug = kwargs.get(kwarg)
	try:
		child = pexpect.spawn('hcitool con')
		child.expect("< LE ",timeout = 1)
		line = child.readline()[:-3].decode().split()[2]
		# line = "B4:99:4C:3A:06:6F handle 71 state 1 lm MASTER"
		# child.sendline("hcitool ledc %s"%line)
		os.system("hcitool ledc %s"%line)
		child.close()
		print("Success delete con")
		return ("Success")
		# pattern_handle4 = re.compile(r"\W([0-9a-fA-F:]+) handle\W([0-9]+) state\W+")
	except Exception as e:
		if debug:
			if debug=="ON":
				print(e)
		print("No device can disconnect")
		child.close()
		return ("Error!")

def pexpect_telnet(ip,password):
	try:
		telconn = pexpect.spawn('telnet %s'%ip)
		# telconn.logfile=sys.stdout
		telconn.expect(":")
		telconn.send("root" + "\r")
		telconn.expect(":", timeout = 3)
		telconn.send(password + "\r")
		telconn.expect("#", timeout = 3)
		print("Success connect iot")
		return (telconn,"Success")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("Error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))
		print("IoTBox Can't connect.")
		telconn.close()
		return (0,"Error")

def pexpect_teldis(child):
	try:
		child.sendline("exit")
		print("Success logout!")
		child.close()
	except Exception as e:
		print(e)
		print("Fail logout")
		child.close()
		return(0,"Error")