import os
import json
import shutil
from datetime import datetime, timezone
from PyQt6.QtCore import *
from dataclasses import *
from .ctags_wrapper import *
from .global_context import *


class Project:
    _config_fname = "config.json"
    _index_fname = "projects.json"
    _console_file = "console.log"

    def __init__(self):
        self.ctags_wrapper:CTagsWrapper = None

        assert GloabalContext.valid() , "Global Context not validated."
        self.project_folder = None
        self.projects_home = GloabalContext.config.storage_settings.path
        print(f"use project base {self.projects_home}")
        GloabalContext.project_config = {}
        self.projects_list = {}
        self.projects_list_path = f"{self.projects_home}/{Project._index_fname}"
        assert bool(self.projects_home)
        self._load_index()
        self.change_listener = None

    def to_dict(self) -> dict:
        return {
            "project_name": self.name(),
            "source": self.source(),
            "codefile_template": self.codefile_template(),
            "lang": self.lang(),
            "last_indexed": self.last_indexed(),
            "project_folder": self.project_folder,
            "ctags_state": self.ctags_wrapper.state_str() if self.ctags_wrapper else "no_ctags"
        }

    @staticmethod
    def to_dict_placeholder() -> dict:
        return {
            "project_name": "NO_PROJECT",
            "source": "",
            "codefile_template": "",
            "lang": "",
            "last_indexed": "",
            "project_folder": "",
            "ctags_state": ""
        }

    def ctagsHandler(self):
        if self.in_project() and self.ctags_wrapper:
            return self.ctags_wrapper.handler
        return None
    def log_handler(self, msg):
        self._log_to_console(msg)

    def in_project(self):
        return bool(self.project_folder) and bool(self.name()) and bool(self.source())
    def set_listener(self, listener):
        self.change_listener = listener

    def on_reindex_done(self, ok:bool):
        if not ok:
            # no need to log. reason already logged
            return
        self._log_to_console(f"reindex done")
        self.update_last_indexed()


    def name(self) -> str:
        return GloabalContext.project_config["name"] if "name" in GloabalContext.project_config else ""

    def source(self) -> str:
        return GloabalContext.project_config["source"] if "source" in GloabalContext.project_config else ""

    def codefile_template(self) -> str:
        return GloabalContext.project_config["template"] if "template" in GloabalContext.project_config else ""

    def lang(self) -> str:
        return GloabalContext.project_config["lang"] if "lang" in GloabalContext.project_config else ""

    def last_indexed(self) -> str:
        if "last_ctag" not in GloabalContext.project_config or int(GloabalContext.project_config["last_ctag"]) <= 0:
            return "never"
        timestamp = float(GloabalContext.project_config["last_ctag"])
        dt_object = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        formatted_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
        return formatted_str

    def update_last_indexed(self):
        GloabalContext.project_config["last_ctag"] = float(datetime.now().timestamp())
        self.save_config()
        self._on_change()

    def _on_change(self):
        if self.change_listener:
            self.change_listener()

    def _is_config_valid(self, cfg: dict) -> bool:
        keys = ["source", "last_ctag", "name"]
        for k in keys:
             if k not in cfg:
                  return False
        return True

    def _log_to_console(self, msg):
        assert GloabalContext.ui_console_controller != None
        GloabalContext.ui_console_controller.addLine(f"[project] {msg}")

    def _enable_console_logging(self):
        assert GloabalContext.ui_console_controller != None
        if not self._check_project_files:
            raise Exception("Not in project")
        GloabalContext.ui_console_controller.setFileOutput(f"{self.projects_home}/{Project._console_file}")

    def _load_index(self):
        self.projects_list = {}
        if not os.path.isfile(self.projects_list_path):
            self._save_index()
            return
        with open(self.projects_list_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.projects_list = data

    def project_from_src(self, src: str)-> str|None :
        s = src.strip()
        if not s:
            raise ValueError('No project name provided')

        if s not in list(self.projects_list.values()):
            return None
        i = list(self.projects_list.values()).index(s)
        keys = list(self.projects_list.keys())[i]
        if not keys:
            return None
        if isinstance(keys, str):
            return keys
        return keys[0]

    def _save_index(self):
        with open(self.projects_list_path, "w", encoding="utf-8") as f:
            json.dump(self.projects_list, f, indent=4, ensure_ascii=False)

    def load_config(self)-> None:
        if not self._check_project_files(self.project_folder):
            raise ValueError('No project configuration file found')
        with open(f"{self.project_folder}/{Project._config_fname}", 'r') as file:
            new_config = json.load(file)
            if self._is_config_valid(new_config):
                GloabalContext.project_config = new_config
            else:
                raise ValueError('Invalid project configuration')

    def save_config(self)-> None:
        if not self._check_project_files(self.project_folder):
            raise ValueError('No project configuration file found')
        if not self._is_config_valid(GloabalContext.project_config):
            raise ValueError('Invalid project configuration')
        with open(f"{self.project_folder}/{Project._config_fname}", 'w') as f:
             json.dump(GloabalContext.project_config, f, indent=4, ensure_ascii=False)


    def reindex(self) -> bool:
        self.init_ctags()
        if self.ctags_wrapper.stage > CTagsWrapperStage.Idle:
            self._log_to_console(f"ctag busy. state:{self.ctags_wrapper.stage.name}")
            return False
        try:
            self.ctags_wrapper.generate_tags(self.on_reindex_done)
        except Exception as e:
            self._log_to_console(f"reindex failed reason: {e}")
            return False
        self._on_change()
        return True

    def init_ctags(self):
        if not self.in_project():
            raise Exception("project not loaded")
        if not self.ctags_wrapper:
            self.ctags_wrapper = CTagsWrapper(self.project_folder, self.source())
            self.ctags_wrapper.log = self.log_handler
            self._log_to_console(f"init ctag - OK")


    def make_project(self, name, src) -> str:
        self.project_folder = f"{self.projects_home}/{name}"
        if os.path.isdir(self.project_folder):
            raise Exception("Project already exists.")
        if not os.path.isdir(src):
            raise Exception("no src dir")
        os.makedirs(self.project_folder)
        initial_data = f"{GloabalContext.app_base}/internal/project_base"
        if not os.path.isdir(initial_data):
            raise Exception("no initial data! app broken")
        shutil.copytree(initial_data, self.project_folder, dirs_exist_ok=True)
        if not self._check_project_files(self.project_folder):
            raise Exception(f"Project in {self.project_folder} doesnt exist or broken.")
        GloabalContext.project_config["source"] = src
        GloabalContext.project_config["last_ctag"] = 0
        GloabalContext.project_config["name"] = name
        self.save_config()
        self.projects_list[name] = src
        self._save_index()
        self._on_change()
        self._enable_console_logging()
        self._log_to_console(f"new project {name}")
        self.init_ctags()
        return self.project_folder

    def _check_project_files(self, folder):
        return all([os.path.isdir(folder),
                    os.path.exists(f'{folder}/config.json')])

    def load_project(self, name: str ):
        print(f"load project {name} in {self.projects_home}")
        self.project_folder = f"{self.projects_home}/{name}"
        if not self._check_project_files(self.project_folder):
            raise Exception(f"Project in {self.project_folder} doesnt exist or broken.")
        self._enable_console_logging()
        self.load_config()
        self._on_change()
        self.init_ctags()
        self._log_to_console(f"load project {name} - OK")



