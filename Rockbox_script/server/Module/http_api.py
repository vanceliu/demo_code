import urllib.request,urllib.parse,urllib.error,time
import logging
from Time_parameter import *
server_conn = {"server":url_conn}

class http_api():
	@staticmethod
	def body2dict(response_read):
		import json
		response_read = bytes.decode(response_read)
		if response_read[0] == "[":
			if len(response_read[1:-1])>0:
				body = json.loads(response_read[1:-1])
			else:
				body = "NaN"
		else:
			if len(response_read)>0:
				body = json.loads(response_read)
			else:
				body = "NaN"
		return body	
	@staticmethod
	def create(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		createUtc = params.get("createUtc")
		params = str.encode(urllib.parse.urlencode(params))
		create = "%s/bstream/api/v1/%s/create"%(http_conn,api_name)
		data = urllib.request.Request(create,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				logger.debug("[SERVER] Update time : %s, Return %s"%(createUtc,body))
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to create api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.debug("Update date : %s, Return %s"%(createUtc,body))
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to create api %s."%api_name)
			return [404,str(e.reason)]

	@staticmethod
	def createBatch(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		headers = {"Content-type": "application/json", "Accept": "application/json"}
		createUtc = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
		# params = str.encode(urllib.parse.urlencode(params))
		params = params.encode('utf-8')
		create = "%s/bstream/api/v1/%s/createBatch"%(http_conn,api_name)
		data = urllib.request.Request(create,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				logger.debug("[SERVER] Update time : %s, Return %s"%(createUtc,body))
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to create api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.debug("Update date : %s, Return %s"%(createUtc,body))
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to create api %s."%api_name)
			return [404,str(e.reason)]
		except Exception as e:
			import sys,os
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logger.warning("[SERVER] Error : %s in line %s,%s"%(e,exc_tb.tb_lineno,fname))

	@staticmethod
	def delete(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		delete = "%s/bstream/api/v1/%s/delete"%(http_conn,api_name)
		data = urllib.request.Request(delete,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to delete api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.debug("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to delete api %s."%(api_name,name))
			return [404,e.reason]

	@staticmethod
	def find(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		find = "%s/bstream/api/v1/%s/find"%(http_conn,api_name)
		data = urllib.request.Request(find,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict and len(body)>4):
				if 'name' in body.keys():
					logger.info("Already exist %s (find)."%(api_name))
				elif 'userName' in body.keys():
					logger.info("Already exist %s (find)."%(api_name))
				logger.debug("[SERVER] find return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to find api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.debug("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to find api %s."%api_name)
			return [404,e.reason]
	
	@staticmethod
	def findById(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		findById = "%s/bstream/api/v1/%s/findById"%(http_conn,api_name)
		data = urllib.request.Request(findById,params,headers)
		try:
			response = opener.open(data,timeout = 10)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				if 'name' in body.keys():
					logger.debug("[SERVER] Already exist %s (findById)."%(api_name))
				elif 'userName' in body.keys():
					logger.debug("[SERVER] Already exist %s (findById)."%(api_name))
				logger.debug("[SERVER] findById Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to findById api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.debug("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to findById api %s."%api_name)
			return [404,e.reason]
	
	@staticmethod
	def findByName(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		findByName = "%s/bstream/api/v1/%s/findByName"%(http_conn,api_name)
		data = urllib.request.Request(findByName,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				if 'name' in body.keys():
					logger.debug("[SERVER] Already exist %s (findByName)."%(api_name))
				elif 'userName' in body.keys():
					logger.debug("[SERVER] Already exist %s (findByName)."%(api_name))
				logger.debug("[SERVER] findByName return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to findByName api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.debug("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib2.error.URLError as e:
			logger.warning("[SERVER] Timeout to findByName api %s."%api_name)
			return [404,e.reason]
	
	@staticmethod
	def login(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		login = "%s/bstream/api/v1/%s/login"%(http_conn,api_name)
		params = str.encode(urllib.parse.urlencode(params))
		data = urllib.request.Request(login,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				if 'name' in body.keys():
					logger.debug("[SERVER] Success login %s."%(api_name))
					logger.debug("[SERVER] Return %s"%body)
				elif 'userName' in body.keys():
					logger.debug("[SERVER] Success login %s."%(api_name))
					logger.debug("[SERVER] Login cookies %s"%response.info().get('Set-cookie'))
					logger.debug("[SERVER] Return %s"%body)
				elif "ok" in body.values():
					logger.info("[SERVER] Success login %s"%api_name)
					logger.debug("[SERVER] Login cookies %s"%response.info().get('Set-cookie'))
				if body.get('onSiteServerUrl'):
					server_conn.update({"server":body.get('onSiteServerUrl')})
				else:
					server_conn.update({"server":url_conn})
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to login api %s by %s."%(api_name,e.code))
			server_conn.update({"server":url_conn})
			body = http_api.body2dict(e.read())
			# logger.info("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			server_conn.update({"server":url_conn})
			logger.warning("[SERVER] Timeout to login api %s."%api_name)
			return [404,str(e.reason)]

	@staticmethod
	def logout(opener,api_name,headers):
		http_conn = server_conn.get("server")
		logout = "%s/bstream/api/v1/%s/logout"%(http_conn,api_name)
		data = urllib.request.Request(logout, data = b"", headers = headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				# logger.info("Success logout %s"%api_name)
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to logout api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.info("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to logout api %s."%api_name)
			return [404,e.reason]

	@staticmethod
	def keepAlive(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		keepAlive = "%s/bstream/api/v1/%s/keepAlive"%(http_conn,api_name)
		params = str.encode(urllib.parse.urlencode(params))
		data = urllib.request.Request(keepAlive, params, headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to keepAlive api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.info("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("Timeout to %s."%api_name)
			return [404,e.reason]

	@staticmethod
	def register(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		register = "%s/bstream/api/v1/%s/register"%(http_conn,api_name)
		data = urllib.request.Request(register,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				if 'name' in body.keys():
					logger.info("[SERVER] Success register api %s."%(api_name))
				elif 'userName' in body.keys():
					logger.info("[SERVER] Success register api %s."%(api_name))
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to register api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.info("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to register api %s."%api_name)
			return [404,e.reason]
	
	@staticmethod
	def update(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		update = "%s/bstream/api/v1/%s/update"%(http_conn,api_name)
		data = urllib.request.Request(update,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				if 'name' in body.keys():
					logger.info("[SERVER] Success update %s."%(api_name))
				elif 'userName' in body.keys():
					logger.info("[SERVER] Success update %s."%(api_name))
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to update api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.info("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to update api %s."%api_name)
			return [404,e.reason]
	
	@staticmethod
	def findOne(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		findOne = "%s/bstream/api/v1/%s/findOne"%(http_conn,api_name)
		data = urllib.request.Request(findOne,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				if 'name' in body.keys():
					logger.info("[SERVER] Success findOne %s."%(api_name))
				elif 'userName' in body.keys():
					logger.info("[SERVER] Success findOne %s."%(api_name))
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to findOne api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.info("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to findOne api %s."%api_name)
			return [404,e.reason]
	
	@staticmethod
	def findWithPage(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		findOne = "%s/bstream/api/v1/%s/findWithPage"%(http_conn,api_name)
		data = urllib.request.Request(findOne,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			body = http_api.body2dict(response.read())
			if (type(body) is dict):
				if 'name' in body.keys():
					logger.info("[SERVER] Success findWithPage %s."%(api_name))
				elif 'userName' in body.keys():
					logger.info("[SERVER] Success findWithPage %s."%(api_name))
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			# logger.warning("Fail to findWithPage api %s by %s."%(api_name,e.code))
			body = http_api.body2dict(e.read())
			# logger.info("Return %s"%body)
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to findWithPage api %s."%api_name)
			return [404,e.reason]

	@staticmethod
	def findRangeWithSelect(opener,api_name,params,headers):
		http_conn = server_conn.get("server")
		params = str.encode(urllib.parse.urlencode(params))
		findRangeWS = "%s/bstream/api/v1/%s/findRangeWithSelect"%(http_conn,api_name)
		data = urllib.request.Request(findRangeWS,params,headers)
		try:
			response = opener.open(data,timeout = 5)
			import json
			body = json.loads(bytes.decode(response.read()))

			if (type(body) is dict):
				if 'name' in body.keys():
					logger.info("[SERVER] Success findRangeWithSelect %s."%(api_name))
				elif 'userName' in body.keys():
					logger.info("[SERVER] Success findRangeWithSelect %s."%(api_name))
				logger.debug("[SERVER] Return %s"%body)
			return [response.getcode(),body]
		except urllib.error.HTTPError as e:
			body = http_api.body2dict(e.read())
			if body.get("message"):
				return [e.code,body.get("message")]
			else:
				return [e.code,e]
		except urllib.error.URLError as e:
			logger.warning("[SERVER] Timeout to findRangeWithSelect api %s."%api_name)
			return [404,e.reason]