from .project import *
from .app_config import *
from .tab_controller import *

class GloabalContext:
    app_base: str = ""
    current_project = None
    config: ConfigManager = None
    ui_globals = None
    ui_skin = None
    ui_project_handler = None
    ui_console_controller = None
    tab_controller: TabController = None
    project_config: None
    qt_env: True

    @staticmethod
    def valid() -> bool:
        if not (GloabalContext.app_base and GloabalContext.config and GloabalContext.ui_console_controller):
            return False
        if GloabalContext.qt_env:
            return bool(GloabalContext.app_base
                        and GloabalContext.config
                        and GloabalContext.ui_globals
                        and GloabalContext.ui_skin
                        and GloabalContext.ui_console_controller
                        and GloabalContext.tab_controller)
        return True
