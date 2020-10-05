# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://cicd.eyesmedia.com.tw/issues/rest/auth/1/session"

# auth = HTTPBasicAuth("vance.liu", "B144DDB3E7A001F66B33995D1DE0D01C")

headers = {
   "Accept": "application/json"
}

data = {
	"username":"vance.liu",
	"password":"28010606"
}

session = requests.session()
response = session.post(url, headers=headers, json=data)
print(response.text)

url = "https://cicd.eyesmedia.com.tw/issues/rest/api/2/issue/NLPTB-54"
response = session.get(url, headers=headers)
print(response.text)
# print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
