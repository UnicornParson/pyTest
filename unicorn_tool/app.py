import sys
import os
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtQml import *
from qml.UnicornUI import *
from internal import *

def load_env():
    default_path: str = "~/utool_data"
    GloabalContext.app_base = os.environ.get("UTOOL_BASE_PATH") or default_path

def load_appconfig():
    if not GloabalContext.app_base:
        raise ValueError("UTOOL_BASE_PATH not set in environment") 
    cfg_name = f"{GloabalContext.app_base}/config.yaml"
    if not os.path.isfile(cfg_name):
        raise ValueError("Config file not found")  
    GloabalContext.config = ConfigManager(config_path=cfg_name)
    GloabalContext.config.load()

class Backend(QObject):
    textChanged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._text = "Нажмите кнопку!"
        
    @pyqtProperty(str, notify=textChanged)
    def labelText(self):
        return self._text
        
    def updateText(self):
        self._text = "Кнопка была нажата!"
        self.textChanged.emit(self._text)

if __name__ == "__main__":
    load_env()
    load_appconfig()
    app = QGuiApplication(sys.argv)
    
    engine = QQmlApplicationEngine()
    TemplatesTypes.register_types()
    backend = Backend()
    app_ico = GloabalContext.app_base + "/img/app_ico.png"
    app.setWindowIcon(QIcon(app_ico))
    window = WindowInfo(800, 600,"My Window", "Main_Window", app_ico, None )
    GloabalContext.ui_skin = Skin(engine)
    GloabalContext.ui_globals = UnicornUIGlobal.self()
    GloabalContext.ui_globals.setPropertyLoggingEnabled = True
    GloabalContext.ui_globals.setDebugGridEnabled = True
    GloabalContext.ui_globals.setFpsBoosterEnabled = True
    
    GloabalContext.tab_controller = TabController() 

    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("wininfo", window)
    engine.rootContext().setContextProperty("skin", GloabalContext.ui_skin)
    engine.rootContext().setContextProperty("globals", GloabalContext.ui_globals)
    engine.rootContext().setContextProperty("tab_controller", GloabalContext.tab_controller)
    
    engine.load("qml/main.qml")
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())