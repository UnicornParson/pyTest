import sqlalchemy as sa
from sqlalchemy.schema import CreateTable
import logging as log
import psycopg2 as pg
from .datatypes import *
import pprint
from .utils import *

class DbCfg:
	def __init__(self):
		self.host = "127.0.0.1",
		self.database_name = "haddan",
		self.user = "haddan",
		self.password = ""
		self.port = 5432

class DBEngine:
	def __init__(self):
		self.tableLatest = "latest"
		self.tableArchive = "archive"
		self.tables = [self.tableLatest, self.tableArchive]
		self.session = None
		self.engine = None
		self.conn = None
		self.cur = None

	def destroy(self):
		if self.cur:
			self.cur.close()
		self.cur = None
		if self.conn:
			self.conn.close()
		self.conn = None

	def connect(self, cfg: DbCfg) -> bool:
		try:
			self.conn = pg.connect(user=cfg.user, password=cfg.password, host=cfg.host, port=cfg.port, dbname=cfg.database_name)
			self.cur = self.conn.cursor()
		except (Exception, pg.Error) as error:
			eprint("cannot connect %s" % str(error.pgerror))
			eprint(error.diag.message_detail)
			self.destroy()
			return False
		except Exception as error:
			eprint("cannot connect %s" % str(error))
			self.destroy()
			return False

		self.engine = sa.create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (cfg.user, cfg.password, cfg.host, cfg.database_name))
		if not self.engine:
			eprint("cannot connect to db")
			self.destroy()
			return False

		return True

	def tryInstall(self) -> bool:
		if not self.engine:
			raise Exception("not connected")

		if self.checkDb():
			# installed
			return True

		log.info("install database")
		metadata_obj = sa.MetaData()
		# FIXME: install views
		# CREATE VIEW public."latestThings"
		#  AS
		# SELECT thingname FROM public.latest GROUP BY thingname ORDER BY thingname;

		latest = sa.Table(
			self.tableLatest, metadata_obj,
			sa.Column('dt', sa.DateTime, index=True, nullable=False),
			sa.Column('shop_id', sa.BigInteger, index=True, nullable=False),
			sa.Column('shop_name', sa.String(1024), nullable=False),
			sa.Column('shop_ownerid', sa.BigInteger, nullable=False),
			sa.Column('shop_opentill', sa.BigInteger, nullable=False),
			sa.Column('shop_money', sa.Integer, nullable=False),
			sa.Column('ttid', sa.BigInteger, index=True, nullable=False),
			sa.Column('thingname', sa.String(512), nullable=False),
			sa.Column('buy', sa.Float, nullable=False),
			sa.Column('sell', sa.Float, nullable=False),
			sa.Column('count', sa.Integer, nullable=False),
			mysql_charset = 'utf8',
			mysql_engine = 'InnoDB'
		)
		archive = sa.Table(
			self.tableArchive, metadata_obj,
			sa.Column('_row', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
			sa.Column('dt', sa.DateTime, index=True, nullable=False),
			sa.Column('shop_id', sa.BigInteger, index=True, nullable=False),
			sa.Column('shop_name', sa.String(1024), nullable=False),
			sa.Column('shop_ownerid', sa.BigInteger, nullable=False),
			sa.Column('shop_opentill', sa.BigInteger, nullable=False),
			sa.Column('shop_money', sa.Integer, nullable=False),
			sa.Column('ttid', sa.BigInteger, index=True, nullable=False),
			sa.Column('thingname', sa.String(512), nullable=False),
			sa.Column('buy', sa.Float, nullable=False),
			sa.Column('sell', sa.Float, nullable=False),
			sa.Column('count', sa.Integer, nullable=False),
			mysql_charset = 'utf8',
			mysql_engine = 'InnoDB'
		)
		metadata_obj.create_all(self.engine)
		return self.checkDb()

	def checkDb(self) -> bool:
		if not self.engine:
			raise Exception("not connected")
		insp = sa.inspect(self.engine)
		ok = True
		for t in self.tables:
			has_table = insp.has_table(t)
			log.debug("test table " + t + ": " + str(has_table))
			ok &= has_table
		return ok

	def getLastThNames(self) -> list:
		if not self.cur:
			eprint("not connected")
			return None
		ret = []
		try:
			self.cur.execute("SELECT thingname FROM public.%s GROUP BY thingname ORDER BY thingname" % self.tableLatest)
			for row in self.cur.fetchall():
				ret.append(row[0])
		except pg.Error as error:
			eprint("cannot insert %s" % str(error.pgerror))
			eprint(error.diag.message_detail)
			self.conn.rollback()
			return None
		except Exception as e:
			eprint("cannot insert (base exception) %s" % str(e))
			self.conn.rollback()
			return None
		return ret
	def flushLatest(self) -> bool:
		if not self.cur:
			eprint("not connected")
			return False
		try:
			# move to archive
			self.cur.execute("""insert into public.%s (dt,shop_id,shop_name,shop_ownerid,shop_opentill,shop_money,ttid,thingname,buy,sell,count)
				select dt,shop_id,shop_name,shop_ownerid,shop_opentill,shop_money,ttid,thingname,buy,sell,count from public.%s"""
			                     %(self.tableArchive, self.tableLatest))
			self.cur.execute("TRUNCATE TABLE  %s" % self.tableLatest)
		except pg.Error as error:
			eprint("cannot insert %s" % str(error.pgerror))
			eprint(error.diag.message_detail)
			self.conn.rollback()
			return False
		except Exception as e:
			eprint("cannot insert (base exception) %s" % str(e))
			self.conn.rollback()
			return False
		self.conn.commit()
		return True

	def tablesStat(self):
		if not self.cur:
			eprint("not connected")
			return None
		ret = {}
		try:
			self.cur.execute("SELECT COUNT(dt) as cnt FROM %s" % self.tableLatest)
			ret['tableLatestCount'] = self.cur.fetchone()[0]
			self.cur.execute("SELECT COUNT(dt) as cnt FROM %s" % self.tableArchive)
			ret['tableArchiveCount'] = self.cur.fetchone()[0]
		except pg.Error as error:
			eprint("cannot insert %s" % str(error.pgerror))
			eprint(error.diag.message_detail)
			self.conn.rollback()
			return None
		except Exception as e:
			eprint("cannot insert (base exception) %s" % str(e))
			self.conn.rollback()
			return None
		return ret

	def applyShop(self, content: list) -> bool:
		if not self.cur:
			eprint("not connected")
			return False
		valuesStr = ""

		for record in content:
			if valuesStr:
				valuesStr += ", "
			valuesStr += str(record.toTuple())
		try:
			q = """INSERT INTO public.%s (dt,shop_id,shop_name,shop_ownerid,shop_opentill,shop_money,ttid,thingname,buy,sell,count) VALUES %s ;""" % \
			    (self.tableLatest, valuesStr)
			self.cur.execute(q)
		except pg.Error as error:
			eprint("cannot insert %s" % str(error.pgerror))
			eprint(error.diag.message_detail)
			self.conn.rollback()
			return False
		except Exception as e:
			eprint("cannot insert (base exception) %s" % str(e))
			self.conn.rollback()
			return False
		self.conn.commit()
		##stmt = sa.insert(self.tableLatest).values(insertList)
		return True
