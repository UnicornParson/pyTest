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
    tab_controller: TabController = None

    @staticmethod
    def valid() -> bool:
        return bool(GloabalContext.app_base 
                    and GloabalContext.config 
                    and GloabalContext.ui_globals 
                    and GloabalContext.ui_skin 
                    and GloabalContext.tab_controller)
