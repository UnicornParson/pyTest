from datetime import datetime
import base64

class GoodRecord:
	def __init__(self):
		self.dt = datetime.now()
		self.shop_id = 0
		self.shop_name = ""
		self.shop_ownerid = 0
		self.shop_opentill = 0
		self.shop_money = 0
		self.ttid = 0
		self.thingname = ""
		self.buy = 0.0
		self.sell = 0.0
		self.count = 0

	def toDict(self) -> dict:
		return {
			"dt": self.dt,
			"shop_id": self.shop_id,
			"shop_name": base64.b64encode(bytes(self.shop_name, 'utf-8')).decode('utf-8'),
			"shop_ownerid": self.shop_ownerid,
			"shop_opentill": self.shop_opentill,
			"shop_money": self.shop_money,
			"ttid": self.ttid,
			"thingname": self.thingname,
			"buy": self.buy,
			"sell": self.sell,
			"count": self.count
		}
	def toTuple(self) -> tuple:
		return (str(self.dt),
		        self.shop_id,
		        base64.b64encode(bytes(self.shop_name, 'utf-8')).decode('utf-8'),
				self.shop_ownerid,
				self.shop_opentill,
				self.shop_money,
				self.ttid,
				self.thingname,
				self.buy,
				self.sell,
				self.count)