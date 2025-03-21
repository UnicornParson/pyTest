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
        self.config = {}
        self.projects_list = {}
        self.projects_list_path = f"{self.projects_home}/{Project._index_fname}"
        assert bool(self.projects_home)
        self._load_index()
        self.change_listener = None
    def set_listener(self, listener):
        self.change_listener = listener

    def name(self) -> str:
        return self.config["name"]
    def source(self) -> str:
        return self.config["source"]
    def last_indexed(self) -> str:
        if "last_ctag" not in self.config or int(self.config["last_ctag"]) <= 0:
            return "never"
        timestamp = float(self.config["last_ctag"])
        dt_object = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        formatted_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
        return formatted_str

        
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
        print(f"@@ keys {keys} t: {type(keys)}")
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
                self.config = new_config
            else:
                raise ValueError('Invalid project configuration')    
            
    def save_config(self)-> None:
        if not self._check_project_files(self.project_folder):
            raise ValueError('No project configuration file found')
        if not self._is_config_valid(self.config):
            raise ValueError('Invalid project configuration')    
        with open(f"{self.project_folder}/{Project._config_fname}", 'w') as f:   
             json.dump(self.config, f) 






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
        self.config["source"] = src
        self.config["last_ctag"] = 0
        self.config["name"] = name
        self.save_config()
        self.projects_list[name] = src
        self._save_index()
        self._on_change()
        self._enable_console_logging()
        self._log_to_console(f"new project {name}")
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
        self._log_to_console(f"load project {name} - OK")



