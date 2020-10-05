# global server setting will write down here
from http.cookiejar import CookieJar
import urllib.request,re,os,threading

# for test_server use
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

# server headeer
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
err_signal = {"signal":404,"Add":0}
IoTBox_raw = os.popen("ifconfig -a").read()
IoTBox_handle = re.compile(r"(.*?)  HWaddr\W([0-9a-fA-F:]+)\W+")
IoTBox_handle2 = re.compile(r"\W+ether\W([0-9a-fA-F:]+)\W+(.*?)")
try:
	IoTBox_info = IoTBox_handle.match(IoTBox_raw)
	IoTBoxMAC = {"mac":IoTBox_info.group(2).replace(":","").upper()}
except:
	IoTBox_info = IoTBox_handle2.search(IoTBox_raw)
	IoTBoxMAC = {"mac":IoTBox_info.group(1).replace(":","").upper()}
relay_login_time = None
relay_ssh_time = None
audio_thread_check = {"check":False,"init":False,"canPlayAudio":False} # check audio thread is working(if working is True) or not(not working is False)
audio_check = {"id":{}} # audio output, every 15 mins if not clear will output again.

Sensor_thread_check = {"check":False} # use for sensor update data thread.

SSS_mode = 1 # 0 means do not create sensorStatistics

connect_status = {} # wifi status
iwconfig_connect_info = {}
relayparams = {} # relay status
WIFITIMECHECK = 600 # wifi check time in second

# ==== do not change this ====
SERVER_check = 0 # server_command connection get error 20 times should reboot
SERVER_internet = 0 # dongle still reset 1 times will reboot 
SERVER_down = 0
SSS = {}

# create cookie handle
cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)
