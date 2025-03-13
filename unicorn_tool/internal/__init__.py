from .project import *
from .app_config import *
from .tab_controller import *


class GloabalContext:
    app_base: str = ""
    current_project: Project = None
    config: ConfigManager = None
    ui_globals = None
    ui_skin = None
    tab_controller: TabController = None

__all__ = ["GloabalContext", "Project", "ConfigManager", "TabController"]