import xml.etree.ElementTree as ET
import urllib.request
import tracemalloc
import logging
import traceback
import pprint
import xmltodict
from datetime import datetime
from .datatypes import *
from .db import *
from .utils import *


class Loader:
	def __init__(self, dbCfg: DbCfg):
		#self.url = "https://haddan.ru/inner/api_shop.php"
		self.url = "http://192.168.0.18/example.xml"
		self.timeout = 30
		self.timetag = "lastupdatetime"
		self.shopTag = "shop"
		self.haddanTag = "haddan"
		self.dbCfg = dbCfg
		self.engine = DBEngine()

	def start(self) -> bool:
		connectRc = self.engine.connect(self.dbCfg)
		if not connectRc:
			eprint("cannot coonect to db")
			self.engine.destroy()
			return False
		return True


	def update(self) -> bool:
		rc = False
		start = datetime.now()
		hdr = {'HTTP_SEC_CH_UA': """ "Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111" """,
		       'HTTP_USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
		       'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
		req = urllib.request.Request(self.url, headers=hdr)
		with urllib.request.urlopen(req, timeout=self.timeout) as f:
			if f.status != 200:
				logging.error("cannot load %s code %d, reason %s", (self.url, f.status, f.reason))
				rc = False
			else:
				content = f.read().decode('utf-8')
				logging.debug("download ok. size %d" % len(content))
				applystart = datetime.now()
				self.engine.flushLatest()
				rc = self.apply(content)
				#print(self.engine.getLastThNames())
				mprint("apply %s duration %s" %(str(rc), str(datetime.now() - applystart)))
		mprint("update data %s duration %s" % (str(rc), str(datetime.now() - start)))
		mprint("STAT: " + str(self.engine.tablesStat()))
		return rc


	def apply(self, content) -> bool:
		doc = xmltodict.parse(content)
		if not doc[self.haddanTag]:
			logging.error("no %s tag" % self.haddanTag)
			return False
		doc = doc[self.haddanTag]
		if not doc['lastupdatetime']:
			logging.error("no lastupdatetime tag")
			return False
		lastupdatetime = doc['lastupdatetime']['@txt']
		lastupdatetime = datetime.strptime(lastupdatetime, '%d-%m-%y %H:%M:%S')
		print(lastupdatetime)
		if not doc[self.shopTag]:
			logging.error("no %s tag" % self.shopTag)
			return False
		shops = doc[self.shopTag]

		for shop in shops:
			rc = self.processShop(shop, lastupdatetime)
			if not rc:
				break
		return True

	def processShop(self, shop, time) -> bool:
		sh_id = shop["@id"]
		sh_name = shop["@name"]
		sh_owner = shop["@ownerid"]
		sh_opentil = shop["@opentill"]
		sh_money = shop["@money"]
		records = []
		if "good" not in shop:
			logging.info("no goods in")
			return True
		s = []
		if type(shop["good"]) is dict:
			s.append(shop["good"])
		else:
			s = shop["good"]
		for good in s:
			if type(good) is not dict:
				print("good not a dict [%s]" % str(good) )
				pprint.pprint(shop)
				return True

			try:
				record = GoodRecord()
				record.ttid = good['ttid']
				record.buy = 0.0
				if 'buy' in good:
					record.buy = good['buy']
				record.sell = 0.0
				if 'sell' in good:
					record.buy = good['sell']
				record.thingname = good['thingname']
				record.count = good['count']
				record.shop_id = sh_id
				record.shop_name = sh_name
				record.shop_ownerid = sh_owner
				record.shop_opentill = sh_opentil
				record.shop_money = sh_money
				record.dt = time
				records.append(record)
			except KeyError as ke:
				log.error("cannot apply good %s reason %s" % (str(good), str(ke)))
				return False
		start = datetime.now()
		applyrc = self.engine.applyShop(records)
		log.debug("apply shop %s - %s. duration %s, result %s" % (sh_id, sh_name, str(datetime.now() - start), str(applyrc)))
		return applyrc

	def selectTtid(self, ttid, data):
		ret = []
		for row in data:
			if row["ttid"] == ttid:
				ret.append(row)
		return ret

	def ttids(self, data):
		pprint.pprint(data)
		ret = []
		for row in data:
			ret.append(row["ttid"])
		return sorted(list(set(ret)))