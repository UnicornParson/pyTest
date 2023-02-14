import json
import os
import requests
from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode


def mlog(level: int, msg: str):
    host = "192.168.0.18"
    port = 1514
    node = str(os.getpid())
    appname = "testapp"
    url = "http://%s:%d/add" % (host, port)
    data = {'e': 'base64',
            'level': level,
            'msg': urlsafe_b64encode(msg.encode('utf8')).decode('utf8'),
            'app': appname, 'node': node}
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'Connection': 'keep-alive',
               'Accept-Encoding': 'gzip, deflate'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.text)


mlog(9, "This will print the headers sent to the server (the default ones, since no other headers are defined).")