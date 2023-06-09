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
from flask import Flask, Response, request, abort, send_from_directory
from bs4 import BeautifulSoup
CONFIG_ROOT = "DEFAULT"

uiapp = None
app = Flask("ShopsUiApp")


@app.route("/", methods=['POST', 'GET'])
def root():
    global uiapp
    if uiapp:
        soup = BeautifulSoup(uiapp.getRoot(request.args), "html.parser")
        return soup.prettify()
    else:
        abort(500)

@app.route('/static/<path:path>')
def send_report(path):
    global uiapp
    if uiapp:
        staticFolder = uiapp.static
        return send_from_directory(staticFolder, path)
    else:
        abort(500)

@app.route('/favicon.ico')
def send_report(path):
    global uiapp
    if uiapp:
        return send_from_directory(uiapp.favicon)
    else:
        abort(500)

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

def checkConfig(cfg) -> bool:
    if not cfg:
        eprint("no cfg")
        return False
    reqKeys = ['dbhost', 'dbuser', 'dbpass', 'dbname', 'uihost', 'uiport']
    for key in reqKeys:
        if key not in cfg:
            eprint("key %s not found in config file" % key)
            return False
    return True


def run() -> int:
    global uiapp
    ret = 0
    config = configparser.ConfigParser()
    bindir = os.path.dirname(os.path.abspath(__file__))
    iniPath = bindir + '/config.ini'
    config.read(iniPath)
    if not config[CONFIG_ROOT]:
        log.error("root " + CONFIG_ROOT + " not found in " + iniPath + " found " + str(config.keys()))
        return -1
    section = config[CONFIG_ROOT]
    if not checkConfig(section):
        eprint("invalid config")
        return -1
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
    if not uiapp:
        uiapp = ShopsUiApp()
    app.run(host=section['uihost'], port=int(section['uiport'].strip()))

    return ret

if __name__ == '__main__':
    log_setup()
    tracemalloc.start()
    result = 0
    try:
        result = run()

    except KeyboardInterrupt:
        eprint(" KeyboardInterrupt...")
    logging.shutdown()
    exit(result)
