import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtQml import *
from qml.UnicornUI import *
from internal import *

def make_absolute(path) -> str:
    expanded_path = os.path.expanduser(path)
    return str(os.path.abspath(expanded_path))
def generate_projname(src:str) -> str:
    folder = os.path.basename(src).strip()
    return f"{folder}_{datetime.now().strftime('%Y.%m.%d.%f')}"
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

def init_project(src_path:str):
    print(f"init project {src_path}")
    GloabalContext.current_project = Project()
    name = GloabalContext.current_project.project_from_src(src_path)
    if not name:
        # create project
        prjname = generate_projname(src_path)
        print(f"new project {prjname}")
        GloabalContext.current_project.make_project(prjname, src_path)
        return prjname
    GloabalContext.current_project.load_project(name)
    GloabalContext.ui_project_handler = ProjectQObject(GloabalContext.current_project)
    return name


def restored_exit(code, folder):
    os.chdir(folder)
    sys.exit(code)

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
    parser = argparse.ArgumentParser(description='Unicorn Tool')
    parser.add_argument('source_path', 
                       type=str, 
                       default=os.getcwd(),
                       help='Path to source directory (optional)',
                       nargs='?')
    args =  parser.parse_args()
    current_dir = os.getcwd()
    
    app = QGuiApplication(sys.argv)
    project_src = args.source_path.strip().replace('\\', '/')
    project_src = make_absolute(project_src)
    print(f"run source {project_src}")
    started_with_src = bool(project_src)
    if project_src and not os.path.isdir(project_src):
        print(f"Source path '{project_src}' not found!")
        restored_exit(-1, current_dir)

    os.chdir(GloabalContext.app_base)
    engine = QQmlApplicationEngine()
    TemplatesTypes.register_types()
    backend = Backend()
    app_ico = GloabalContext.app_base + "/img/app_ico.png"
    app.setWindowIcon(QIcon(app_ico))
    window = WindowInfo(800, 600,"Unicorn tool", "Main_Window", app_ico, None )
    
    GloabalContext.ui_skin = Skin(engine)
    GloabalContext.ui_globals = UnicornUIGlobal.self()
    GloabalContext.ui_globals.setPropertyLoggingEnabled = True
    GloabalContext.ui_globals.setDebugGridEnabled = True
    GloabalContext.ui_globals.setFpsBoosterEnabled = True
    GloabalContext.ui_console_controller = ConsoleController()
    GloabalContext.tab_controller = TabController() 

    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("wininfo", window)
    engine.rootContext().setContextProperty("skin", GloabalContext.ui_skin)
    engine.rootContext().setContextProperty("globals", GloabalContext.ui_globals)
    engine.rootContext().setContextProperty("tab_controller", GloabalContext.tab_controller)
    
    engine.rootContext().setContextProperty("console_controller", GloabalContext.ui_console_controller)
    
    engine.load("qml/main.qml")
    if not engine.rootObjects():
        restored_exit(-1, current_dir)
    
    prjname = init_project(project_src)
    engine.rootContext().setContextProperty("project", GloabalContext.ui_project_handler)
    window.name = prjname
    rc = app.exec()
    restored_exit(rc, current_dir)