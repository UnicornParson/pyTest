import subprocess
import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Union

class CTagsWrapper:
    tags_db = "tags.db"
    tags_plain = "tags.txt"

    def __init__(self, project_folder:str, source_target:str):
        self.ctags_path = "ctags"
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
        try:
            subprocess.run(
                [self.ctags_path, "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(f"ctags not found at '{self.ctags_path}'. Install with 'sudo apt install universal-ctags'")

    def generate_tags(self):
        cmd = f"{self.ctags_path} -R -f {self.plain_output_path} {self.source_target}"
        try:
            subprocess.run(cmd, check=True)
            print(f"Tags generated successfully: {Path(self.plain_output_path).resolve()}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ctags failed with error: {e}")
        
        # check results
        if not os.path.isfile(self.plain_output_path):
            raise RuntimeError("ctags did not generate any tags")
        
        print("convert tags")
        self.convert_report(self.plain_output_path)

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

        with open(self.plain_output_path, 'r') as f:
            for line in f:
                fields = self._parse_ctags_line(line)
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
        cur.execute('VACUUM')
        self._put_cur()
