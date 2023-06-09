from flask import Flask, Response
import os
import pathlib
from .utils import *

class ShopsUiApp:
    def __init__(self):
        self.templatesFolder = str(pathlib.Path(__file__).parent.absolute()) + "/html"
        self.static = str(pathlib.Path(__file__).parent.absolute()) + "/static"
        self.favicon = self.static + "/favicon.ico"
        self.appname = "Haddan Shop UI"
        self.templates = {}
        templatesPathes = {
            "header": "header.htm",
            "footer": "footer.htm"
        }
        for key, fname in templatesPathes.items():
            loadrc = self.readTemplate(key, fname)
            if not loadrc:
                eprint("cannot load %s" % key)
                raise SystemError
            mprint("loading templates: OK")


    def readTemplate(self, key: str, fname: str) -> bool:
        path = self.templatesFolder + "/" + fname
        if not os.path.isfile(path):
            eprint("cannot find template file %s" % path)
            return False
        contents = pathlib.Path(path).read_text()
        self.templates[key] = contents
        return True



    def getRoot(self, args):
        print(pathlib.Path(__file__).parent.absolute())
        html = self.templates["header"] % self.appname

        html += self.templates["footer"]
        return html
