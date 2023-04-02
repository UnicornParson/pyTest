from internal import *
import tracemalloc
import logging as log
import traceback
import configparser
import asyncio
import time
import os
import configparser
from logging.handlers import *
CONFIG_ROOT = "DEFAULT"

def log_setup():
    #fname = 'shops.%d.log' % (round(time.time() * 1000))
    #log_handler = logging.handlers.WatchedFileHandler(fname)
    maxBytes = 200 * 2**20 #200mb
    log_handler = log.handlers.RotatingFileHandler("shops.log", mode='a', maxBytes=maxBytes, backupCount=20)
    formatter = log.Formatter(
        '%(asctime)s [%(process)d]: %(message)s',
        '%d-%m-%y %H:%M:%S')
    formatter.converter = time.gmtime  # if you want UTC time
    log_handler.setFormatter(formatter)
    logger = log.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

async def main() -> int:
    ret = 0
    config = configparser.ConfigParser()
    bindir = os.path.dirname(os.path.abspath(__file__))
    iniPath = bindir + '/config.ini'
    config.read(iniPath)
    if not config[CONFIG_ROOT]:
        log.error("root " + CONFIG_ROOT + " not found in " + iniPath + " found " + str(config.keys()))
        return -1
    section = config[CONFIG_ROOT]
    dbcfg = DbCfg()
    dbcfg.host = section['dbhost']
    dbcfg.user = section['dbuser']
    dbcfg.password = section['dbpass']
    dbcfg.database_name = section['dbname']


    engine = DBEngine()
    connect_rc = engine.connect(dbcfg)
    if not connect_rc:
        eprint("cannot connect to db")
        engine.destroy()
        return -1

    if not engine.tryInstall():
        eprint("broken db. cannot install")
        engine.destroy()
        return -1
    engine.destroy()

    l = Loader(dbcfg)
    rc = l.start()
    if not rc:
        eprint("cannot start loader")
        return -1
    rc = l.update()
    if not rc:
        eprint("cannot load")
        return -1
    return ret


if __name__ == '__main__':
    log_setup()
    tracemalloc.start()
    result = 0
    try:
        result = asyncio.run(main())
    except KeyboardInterrupt:
        eprint(" KeyboardInterrupt...")
    logging.shutdown()
    exit(result)
