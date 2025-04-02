import subprocess
import os
import json
import sqlite3
from tqdm import tqdm
from time import time
from pathlib import Path
from typing import List, Dict, Optional, Union
from PyQt6.QtCore import *
from enum import Enum
from .global_context import *
from .utils import Utils

class CTagsWrapperStage(Enum):
    NotSet = -1
    Idle = 0
    Failed = 1
    Starting = 2
    CtagsActive = 3
    ConvertationToDb = 4
    Done = 10

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.value > other.value
        return NotImplemented
    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.value > other.value
        return NotImplemented

class CTagsWrapperSignalHandler(QObject):
    activityChanged = pyqtSignal(bool)
    stageChanged = pyqtSignal(bool)
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._ctags_active = False
        self._ctags_stage = 0
    
    @pyqtProperty(int, notify=stageChanged)
    def ctags_stage(self):
        return self._ctags_stage

    @ctags_stage.setter
    def ctags_stage(self, value):
        if self.ctags_active != value:
            self.ctags_active = value
            self.stageChanged.emit(value)


    @pyqtProperty(int, notify=activityChanged)
    def ctags_active(self):
        return self._ctags_active
    @ctags_active.setter
    def ctags_active(self, value):
        if self._ctags_active != value:
            self._ctags_active = value
            self.activityChanged.emit(value)

class CTagsWrapper:
    tags_db = "tags.db"
    tags_plain = "tags.txt"

    def __init__(self, project_folder:str, source_target:str):
        self.log = None
        self.ctags_path = GloabalContext.config.system_settings.ctags_bin
        self.project_folder = project_folder   
        self.source_target = source_target
        if not os.path.isdir(self.project_folder):
            raise Exception("Project folder does not exist")
        if not os.path.isdir(self.source_target):
            raise Exception("Source target does not exist")   

        self._check_ctags_available()
        self.project_folder = project_folder   
        self.source_target = source_target
        self.db_path = os.path.join(project_folder , CTagsWrapper.tags_db)
        self.plain_output_path = os.path.join(project_folder , CTagsWrapper.tags_plain)
        self.conn = None
        self.cursor = None
        self.cursor_counter = 0
        self.handler = CTagsWrapperSignalHandler()
        self.stage = CTagsWrapperStage.Idle

        self._reindex_listener = None
        

    def print(self, msg):
        if self.log:
            self.log(msg)

    def _set_stage(self, value:CTagsWrapperStage):
        self.stage = value
        i = value.value
        self.handler.ctags_stage = i
        self.handler.ctags_active = (1 if (value in [
                                CTagsWrapperStage.CtagsActive,
                                CTagsWrapperStage.Starting,
                                CTagsWrapperStage.ConvertationToDb]) else 0)


    def _get_cur(self):
        if not self._has_tag_db():
            raise RuntimeError("No tag database found. project dir broken.")
        if self.cursor:
            self.cursor_counter += 1
            return self.cursor
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor_counter = 1
        return self.cursor
    def _cur_commit(self) -> None:
        if not self.cursor or not self.conn:
            raise Exception("No cursor or connection found")    
        self.conn.commit()    

    def _put_cur(self) -> None:
        if not self.cursor:
            self.cursor_counter = 0
            return
        self.cursor_counter -= 1

        if self.cursor_counter <= 0:
            self.cursor = None
            self.cursor_counter = 0
            if self.conn:
                self.conn.close()
                self.conn = None

    def _tags_count(self):
        cur = self._get_cur()
        cur.execute('''SELECT COUNT(*) as cnt FROM tags''')
        row = cur.fetchone()
        self._put_cur()
        return int(row[0])

    def _has_tag_db(self):
        return os.path.isfile(self.db_path)
    
    def _check_ctags_available(self):
        self.print(f"start ctag")
        try:
            subprocess.run(
                [self.ctags_path, "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(f"ctags not found at '{self.ctags_path}'. Install with 'sudo apt install universal-ctags'")
    
    def on_ctags_done(self, return_code, stdout, stderr):
        self.print(f"ctags done rc:{return_code}")
        self.print(f"ctags stderr:{stderr}")
        if return_code:
            self._set_stage(CTagsWrapperStage.Failed)
            return
        if not os.path.isfile(self.plain_output_path):
            self._set_stage(CTagsWrapperStage.Failed)
            self.print(f"ctags did not generate any tags in {Path(self.plain_output_path).resolve()}")
            if self._reindex_listener:
                self._reindex_listener(False)
            raise RuntimeError("ctags did not generate any tags")
        
        self.print(f"Tags generated successfully: {Path(self.plain_output_path).resolve()}")
        ts = time()
        self.print("convert tags")
        self._set_stage(CTagsWrapperStage.CtagsActive)

        self.convert_report(self.plain_output_path)
        te = time()
        self.print(f"tags converted took {float(te-ts):0.4f}")
        self.handler.ctags_active = False

        if self._reindex_listener:
            self._reindex_listener(True)

    def generate_tags(self, listener = None):
        self._set_stage(CTagsWrapperStage.Starting)
        self._reindex_listener = listener
        try:
            self._set_stage(CTagsWrapperStage.CtagsActive)
            Utils.run_command_async([self.ctags_path, "--output-encoding=utf-8", "-R", "-f", self.plain_output_path, self.source_target],
                                    self.on_ctags_done)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ctags failed with error: {e}")

    def _parse_ctags_line(self, line):
        line = line.strip()
        if not line or line.startswith('!'):
            return None
        
        parts = line.split('\t', 3)
        if len(parts) < 3:
            return None
        
        name, path, pattern = parts[0], parts[1], parts[2].rstrip(';"')
        fields = {
            'name': name,
            'path': path,
            'pattern': pattern,
            'line': None,
            'typeref': None,
            'roles': None,
            'extras': None,
            '_type': None
        }
        
        if len(parts) > 3:
            for field in parts[3].split('\t'):
                if ':' in field:
                    key, value = field.split(':', 1)
                    key = key.strip().lower()
                    fields[key] = value.strip()
        if 'line' in fields:
            try:
                fields['line'] = int(fields['line'])
            except (ValueError, TypeError):
                fields['line'] = None
        return fields

    def has_tag_data(self):
        return bool(self._tags_count() > 0)

    def convert_report(self, report_file):
        if not os.path.isfile(self.plain_output_path):
            raise RuntimeError("no ctags plain report")
        cur = self._get_cur()
        if self.has_tag_data():
            cur.execute('DELETE FROM tags')

        with open(self.plain_output_path, 'rb') as f:
            total_lines = Utils.lines_in(self.plain_output_path)
            lnum = 0
            for line_bytes in tqdm(f, total=total_lines, desc="Loading tags"):
                lnum += 1
                try:
                    line_str = line_bytes.decode('utf-8', errors='replace').strip()
                    #line_str = line.decode('utf-8')
                    fields = self._parse_ctags_line(line_str)

                except UnicodeDecodeError:
                    # Skip the problematic line and continue with the next one
                    self.print(f"Skipping line due to UnicodeDecodeError l {lnum}")
                    continue

                if not fields:
                    continue
                
                cur.execute('''
                    INSERT INTO tags (
                        name, path, kind, line, language,
                        scope, pattern, typeref, roles, extras, _type
                    ) VALUES (
                        :name, :path, :kind, :line, :language,
                        :scope, :pattern, :typeref, :roles, :extras, :_type
                    )
                ''', {
                    'name': fields['name'],
                    'path': fields['path'],
                    'kind': fields.get('kind'),
                    'line': fields.get('line'),
                    'language': fields.get('language'),
                    'scope': fields.get('scope'),
                    'pattern': fields.get('pattern'),
                    'typeref': fields.get('typeref'),
                    'roles': fields.get('roles'),
                    'extras': fields.get('extras'),
                    '_type': fields.get('_type')
                })
        self._cur_commit()
        self.print(f"found {lnum} records")
        self.print("optimize tags db")
        cur.execute('VACUUM')
        self._put_cur()
